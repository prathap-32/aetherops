# services/requirement_analysis/app/sync_helper.py
import logging
import httpx
import asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import EC2Catalog, RDSCatalog, GenericServiceCatalog
from app.cache import cache_manager

logger = logging.getLogger("requirement-analysis-sync")

GENERIC_SERVICES_ITEMS = {
    "iam": [
        "IAM User",
        "IAM Role",
        "IAM Policy"
    ],
    "vpc": [
        "NAT Gateway",
        "VPN Connection",
        "Transit Gateway",
        "VPC Peering",
        "Elastic IP"
    ],
    "s3": [
        "Standard Storage",
        "Infrequent Access Storage",
        "One Zone-IA Storage",
        "Glacier Storage",
        "Glacier Deep Archive",
        "Intelligent-Tiering"
    ],
    "route53": [
        "Hosted Zone",
        "Standard Query",
        "Latency Query",
        "Geo Query"
    ],
    "ebs": [
        "gp3 Volume",
        "gp2 Volume",
        "io2 Volume",
        "st1 Volume",
        "sc1 Volume"
    ],
    "efs": [
        "Standard Storage",
        "Infrequent Access",
        "Archive Storage"
    ],
    "eks": [
        "EKS Cluster",
        "Fargate Pod",
        "Fargate Memory"
    ],
    "ecs": [
        "Fargate vCPU",
        "Fargate Memory",
        "Fargate Spot vCPU",
        "Fargate Spot Memory"
    ],
    "ecr": [
        "Registry Storage",
        "Data Transfer Out"
    ],
    "waf": [
        "Web ACL",
        "Rule",
        "Request"
    ],
    "cloudwatch": [
        "Metric",
        "Alarms",
        "Dashboard",
        "Log Ingestion"
    ],
    "cloudfront": [
        "Data Transfer Out",
        "HTTP Requests",
        "HTTPS Requests"
    ],
    "cloudtrail": [
        "Paid Events",
        "Insights"
    ]
}

async def sync_catalog_from_aws(db: AsyncSession, region: str = "us-east-1") -> dict:
    """
    Fetches the latest EC2 and RDS pricing from live AWS and community APIs,
    updates the database tables (replacing existing records), and invalidates the Redis Cache.
    """
    region = region.lower().strip()
    # 1. Fetch EC2 pricing from ec2.shop
    logger.info(f"Fetching EC2 pricing from ec2.shop for region {region}...")
    ec2_url = f"https://ec2.shop?region={region}"
    headers = {"Accept": "application/json"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.get(ec2_url, headers=headers)
            res.raise_for_status()
            ec2_raw = res.json()
            if isinstance(ec2_raw, dict):
                ec2_data = ec2_raw.get("Prices", [])
            else:
                ec2_data = ec2_raw
    except Exception as e:
        logger.error(f"Failed to fetch EC2 pricing: {e}")
        raise RuntimeError(f"EC2 fetch failed: {str(e)}")

    # 2. Fetch RDS pricing from AWS Price List Bulk API
    logger.info(f"Fetching RDS pricing from AWS Price List Bulk API for region {region}...")
    rds_url = f"https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/{region}/index.json"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.get(rds_url)
            res.raise_for_status()
            rds_data = res.json()
    except Exception as e:
        logger.error(f"Failed to fetch RDS pricing: {e}")
        raise RuntimeError(f"RDS fetch failed: {str(e)}")

    # 3. Parse EC2 data
    ec2_db_items = {}
    for item in ec2_data:
        try:
            instance_type = item.get("InstanceType")
            if not instance_type:
                continue
            
            # Parse RAM
            mem_str = item.get("Memory", "0 GiB")
            ram_gb = 0.0
            if "GiB" in mem_str:
                ram_gb = float(mem_str.replace("GiB", "").strip())
            
            vcpus = int(item.get("VCPUS", 0))
            
            # Handle Price
            cost_val = item.get("Cost")
            if cost_val is None or str(cost_val).upper() == "NA":
                price_per_hour = 0.0
            else:
                price_per_hour = float(cost_val)
                
            network_performance = item.get("Network", "Up to 10 Gbps")
            
            # Categorize based on prefix
            instance_lower = instance_type.lower()
            if instance_lower.startswith(("t2.", "t3.", "t4g.", "t3a.", "t1.")):
                category = "burstable"
            elif instance_lower.startswith(("c4.", "c5.", "c6.", "c7.", "c8.")):
                category = "compute"
            elif instance_lower.startswith(("r4.", "r5.", "r6.", "r7.", "r8.")):
                category = "memory"
            elif instance_lower.startswith(("g4.", "g5.", "g6.", "p3.", "p4.", "p5.")):
                category = "gpu"
            elif instance_lower.startswith(("m4.", "m5.", "m6.", "m7.", "m8.", "a1.")):
                category = "general"
            else:
                # Fallback check
                if "t" in instance_lower.split(".")[0]:
                    category = "burstable"
                elif "c" in instance_lower.split(".")[0]:
                    category = "compute"
                elif "r" in instance_lower.split(".")[0]:
                    category = "memory"
                elif "g" in instance_lower.split(".")[0] or "p" in instance_lower.split(".")[0]:
                    category = "gpu"
                else:
                    category = "general"

            if price_per_hour <= 0.0 or vcpus <= 0 or ram_gb <= 0.0:
                continue

            new_item = EC2Catalog(
                instance_type=instance_type,
                vcpus=vcpus,
                ram_gb=ram_gb,
                price_per_hour=price_per_hour,
                network_performance=network_performance,
                category=category
            )
            if instance_type not in ec2_db_items or price_per_hour < ec2_db_items[instance_type].price_per_hour:
                ec2_db_items[instance_type] = new_item
        except Exception as e:
            logger.warning(f"Error parsing EC2 item {item}: {e}")
            continue

    # 4. Parse RDS data
    rds_db_items = {}
    products = rds_data.get("products", {})
    terms = rds_data.get("terms", {}).get("OnDemand", {})

    for sku, product in products.items():
        try:
            family = product.get("productFamily")
            if family != "Database Instance":
                continue
            
            attrs = product.get("attributes", {})
            engine = attrs.get("databaseEngine")
            if attrs.get("deploymentOption") != "Single-AZ":
                continue
            if engine not in ["MySQL", "PostgreSQL"]:
                continue
                
            instance_type = attrs.get("instanceType")
            if not instance_type:
                continue
                
            vcpus = int(attrs.get("vcpu", 0))
            
            # Parse RAM
            mem_str = attrs.get("memory", "0 GiB")
            ram_gb = 0.0
            if "GiB" in mem_str:
                ram_gb = float(mem_str.replace("GiB", "").strip())
                
            # Get On-Demand price
            sku_terms = terms.get(sku, {})
            price_per_hour = 0.0
            for term_id, term_details in sku_terms.items():
                price_dimensions = term_details.get("priceDimensions", {})
                for rate_code, rate_details in price_dimensions.items():
                    unit = rate_details.get("unit")
                    if unit == "Hrs":
                        price_str = rate_details.get("pricePerUnit", {}).get("USD", "0.0")
                        price_per_hour = float(price_str)
                        break
            
            # Skip instances with zero price or invalid vcpus/ram
            if price_per_hour <= 0.0 or vcpus <= 0 or ram_gb <= 0.0:
                continue

            # Categorize RDS
            instance_lower = instance_type.lower()
            if "db.t" in instance_lower:
                category = "burstable"
            elif "db.r" in instance_lower or "db.x" in instance_lower:
                category = "memory"
            else:
                category = "standard"

            new_item = RDSCatalog(
                instance_type=instance_type,
                vcpus=vcpus,
                ram_gb=ram_gb,
                price_per_hour=price_per_hour,
                category=category
            )
            if instance_type not in rds_db_items or price_per_hour < rds_db_items[instance_type].price_per_hour:
                rds_db_items[instance_type] = new_item
        except Exception as e:
            logger.warning(f"Error parsing RDS product {sku}: {e}")
            continue

    if not ec2_db_items or not rds_db_items:
        raise ValueError(f"Sync generated empty results (EC2 count: {len(ec2_db_items)}, RDS count: {len(rds_db_items)})")

    # 4.5. Resolve Generic Services Catalog Items
    logger.info("Syncing generic AWS services items...")
    generic_db_items = []
    http_cache = {}
    http_cache_tasks = {}
    
    items_to_lookup = []
    for service_name, item_types in GENERIC_SERVICES_ITEMS.items():
        for item_type in item_types:
            items_to_lookup.append((service_name, item_type))
            
    async def run_lookup(svc, item_t):
        try:
            res_spec = await lookup_generic_aws_service(svc, item_t, region=region, cache=http_cache, cache_tasks=http_cache_tasks)
            db_item = GenericServiceCatalog(
                service=svc,
                instance_type=res_spec["instance_type"],
                vcpus=res_spec["vcpus"],
                ram_gb=res_spec["ram_gb"],
                price_per_hour=res_spec["price_per_hour"],
                unit=res_spec["unit"],
                category=res_spec["category"],
                region=res_spec["region"],
                details=res_spec["details"]
            )
            return db_item
        except Exception as ex:
            logger.warning(f"Error during async lookup of {svc} - {item_t}: {ex}")
            fallback_item = get_generic_fallback_pricing(svc, item_t, region=region)
            return GenericServiceCatalog(
                service=svc,
                instance_type=fallback_item["instance_type"],
                vcpus=fallback_item["vcpus"],
                ram_gb=fallback_item["ram_gb"],
                price_per_hour=fallback_item["price_per_hour"],
                unit=fallback_item["unit"],
                category=fallback_item["category"],
                region=fallback_item["region"],
                details=fallback_item["details"]
            )

    lookup_tasks = [run_lookup(svc, item_t) for svc, item_t in items_to_lookup]
    generic_db_items = await asyncio.gather(*lookup_tasks)

    # 5. Overwrite the tables inside a single database transaction
    logger.info(f"Writing {len(ec2_db_items)} EC2, {len(rds_db_items)} RDS, and {len(generic_db_items)} generic service items to database...")
    await db.execute(delete(EC2Catalog))
    await db.execute(delete(RDSCatalog))
    await db.execute(delete(GenericServiceCatalog))
    
    db.add_all(ec2_db_items.values())
    db.add_all(rds_db_items.values())
    db.add_all(generic_db_items)
    await db.commit()

    # 6. Clear Redis Cache
    cache_cleared = await cache_manager.clear_catalog_cache()

    logger.info(f"Database synced successfully. Cache cleared: {cache_cleared}")
    return {
        "status": "success",
        "added_ec2": len(ec2_db_items),
        "updated_ec2": 0,
        "added_rds": len(rds_db_items),
        "updated_rds": 0,
        "added_generic": len(generic_db_items),
        "cache_cleared": cache_cleared
    }


def _categorize_ec2(instance_type: str) -> str:
    """Classify an EC2 instance type into a category based on its prefix."""
    instance_lower = instance_type.lower()
    if instance_lower.startswith(("t2.", "t3.", "t4g.", "t3a.", "t1.")):
        return "burstable"
    elif instance_lower.startswith(("c4.", "c5.", "c6.", "c7.", "c8.")):
        return "compute"
    elif instance_lower.startswith(("r4.", "r5.", "r6.", "r7.", "r8.")):
        return "memory"
    elif instance_lower.startswith(("g4.", "g5.", "g6.", "p3.", "p4.", "p5.")):
        return "gpu"
    elif instance_lower.startswith(("m4.", "m5.", "m6.", "m7.", "m8.", "a1.")):
        return "general"
    else:
        prefix = instance_lower.split(".")[0]
        if "t" in prefix:
            return "burstable"
        elif "c" in prefix:
            return "compute"
        elif "r" in prefix:
            return "memory"
        elif "g" in prefix or "p" in prefix:
            return "gpu"
        return "general"


def _categorize_rds(instance_type: str) -> str:
    """Classify an RDS instance type into a category based on its prefix."""
    instance_lower = instance_type.lower()
    if "db.t" in instance_lower:
        return "burstable"
    elif "db.r" in instance_lower or "db.x" in instance_lower:
        return "memory"
    return "standard"


def _get_region_from_az_and_region(region: str = None, az: str = None) -> str:
    if region:
        return region
    if az:
        if len(az) > 1 and az[-1].isalpha() and az[-2].isdigit():
            return az[:-1]
        return az
    return "us-east-1"


async def lookup_ec2_instance(instance_type: str, region: str = "us-east-1", az: str = None) -> dict:
    """
    Fetches live specs for a single EC2 instance type from ec2.shop.
    Returns a dict with vcpus, ram_gb, price_per_hour, network_performance, category.
    Raises ValueError if not found.
    """
    target_region = _get_region_from_az_and_region(region, az)
    logger.info(f"Looking up EC2 instance '{instance_type}' from ec2.shop for region {target_region}...")
    ec2_url = f"https://ec2.shop?region={target_region}&filter={instance_type}"
    headers = {"Accept": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(ec2_url, headers=headers)
            res.raise_for_status()
            ec2_raw = res.json()
            prices = ec2_raw.get("Prices", []) if isinstance(ec2_raw, dict) else ec2_raw
    except Exception as e:
        logger.error(f"ec2.shop lookup failed: {e}")
        raise RuntimeError(f"EC2 lookup failed: {str(e)}")

    # Find exact match
    for item in prices:
        if item.get("InstanceType", "").lower() == instance_type.lower():
            mem_str = item.get("Memory", "0 GiB")
            ram_gb = float(mem_str.replace("GiB", "").strip()) if "GiB" in mem_str else 0.0
            vcpus = int(item.get("VCPUS", 0))
            cost_val = item.get("Cost")
            price = float(cost_val) if cost_val and str(cost_val).upper() != "NA" else 0.0
            network = item.get("Network", "Up to 10 Gbps")
            category = _categorize_ec2(instance_type)

            if vcpus <= 0 or ram_gb <= 0.0 or price <= 0.0:
                raise ValueError(f"Invalid specs for '{instance_type}': vCPUs={vcpus}, RAM={ram_gb}, Price={price}")

            return {
                "instance_type": item.get("InstanceType"),
                "vcpus": vcpus,
                "ram_gb": ram_gb,
                "price_per_hour": price,
                "network_performance": network,
                "category": category
            }

    raise ValueError(f"EC2 instance type '{instance_type}' not found in ec2.shop {target_region} pricing data.")


async def lookup_rds_instance(instance_type: str, region: str = "us-east-1", az: str = None) -> dict:
    """
    Fetches live specs for a single RDS instance type from the AWS Bulk Pricing API.
    Returns a dict with vcpus, ram_gb, price_per_hour, category.
    Raises ValueError if not found.
    """
    target_region = _get_region_from_az_and_region(region, az)
    logger.info(f"Looking up RDS instance '{instance_type}' from AWS Pricing API for region {target_region}...")
    rds_url = f"https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/{target_region}/index.json"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.get(rds_url)
            res.raise_for_status()
            rds_data = res.json()
    except Exception as e:
        logger.error(f"AWS RDS pricing lookup failed: {e}")
        raise RuntimeError(f"RDS lookup failed: {str(e)}")

    products = rds_data.get("products", {})
    terms = rds_data.get("terms", {}).get("OnDemand", {})

    best_match = None
    best_price = float("inf")

    for sku, product in products.items():
        if product.get("productFamily") != "Database Instance":
            continue
        attrs = product.get("attributes", {})
        if attrs.get("deploymentOption") != "Single-AZ":
            continue
        if attrs.get("databaseEngine") not in ["MySQL", "PostgreSQL"]:
            continue
        if attrs.get("instanceType", "").lower() != instance_type.lower():
            continue

        vcpus = int(attrs.get("vcpu", 0))
        mem_str = attrs.get("memory", "0 GiB")
        ram_gb = float(mem_str.replace("GiB", "").strip()) if "GiB" in mem_str else 0.0

        # Extract price
        sku_terms = terms.get(sku, {})
        price_per_hour = 0.0
        for term_id, term_details in sku_terms.items():
            for rate_code, rate_details in term_details.get("priceDimensions", {}).items():
                if rate_details.get("unit") == "Hrs":
                    price_per_hour = float(rate_details.get("pricePerUnit", {}).get("USD", "0.0"))
                    break

        if price_per_hour <= 0.0 or vcpus <= 0 or ram_gb <= 0.0:
            continue

        # Keep cheapest match
        if price_per_hour < best_price:
            best_price = price_per_hour
            best_match = {
                "instance_type": attrs.get("instanceType"),
                "vcpus": vcpus,
                "ram_gb": ram_gb,
                "price_per_hour": price_per_hour,
                "category": _categorize_rds(instance_type)
            }

    if not best_match:
        raise ValueError(f"RDS instance type '{instance_type}' not found in AWS Pricing API (MySQL/PostgreSQL, Single-AZ, {target_region}).")

    return best_match


SERVICE_OFFER_CODES = {
    "s3": "AmazonS3",
    "efs": "AmazonEFS",
    "route53": "AmazonRoute53",
    "route 53": "AmazonRoute53",
    "cloudwatch": "AmazonCloudWatch",
    "cloudfront": "AmazonCloudFront",
    "cloudtrail": "AWSCloudTrail",
    "eks": "AmazonEKS",
    "ecs": "AmazonECS",
    "ecr": "AmazonECR",
    "waf": "awswaf",
}


def get_generic_fallback_pricing(service: str, item_type: str, region: str = "us-east-1") -> dict:
    service = service.lower()
    item_type_lower = item_type.lower() if item_type else ""
    region_lower = region.lower().strip() if region else "us-east-1"
    
    # Region multipliers to scale base pricing to match regional rates
    multipliers = {
        "us-east-1": 1.0,
        "us-west-2": 1.02,
        "eu-west-1": 1.08,
        "ap-southeast-1": 1.25,
        "ap-south-1": 1.10
    }
    m = multipliers.get(region_lower, 1.0)
    
    price = 0.0
    unit = "Hrs"
    category = "general"
    details = f"Static price for {service} {item_type}"
    
    if service == "s3":
        category = "storage"
        unit = "GB-Month"
        if "glacier" in item_type_lower:
            price = round(0.0036 * m, 5)
        else:
            price = round(0.023 * m, 5)
    elif service == "ebs":
        category = "storage"
        unit = "GB-Month"
        if "gp3" in item_type_lower:
            price = round(0.08 * m, 5)
        else:
            price = round(0.10 * m, 5)
    elif service == "efs":
        category = "storage"
        unit = "GB-Month"
        price = round(0.30 * m, 5)
    elif service == "vpc":
        category = "networking"
        if "nat" in item_type_lower:
            price = round(0.045 * m, 5)
        else:
            price = round(0.05 * m, 5)
    elif service in ["route53", "route 53"]:
        category = "networking"
        unit = "HostedZone-Month"
        price = round(0.50 * m, 5)
    elif service == "eks":
        category = "compute"
        price = round(0.10 * m, 5)
    elif service == "ecs":
        category = "compute"
        price = round(0.01 * m, 5)
    elif service == "ecr":
        category = "storage"
        unit = "GB-Month"
        price = round(0.10 * m, 5)
    elif service == "waf":
        category = "security"
        price = round(0.008 * m, 5)
    elif service == "cloudwatch":
        category = "monitoring"
        price = round(0.30 * m, 5)
    elif service == "cloudfront":
        category = "networking"
        unit = "GB-Month"
        price = round(0.085 * m, 5)
    elif service == "cloudtrail":
        category = "monitoring"
        price = 0.0
        
    return {
        "instance_type": item_type,
        "vcpus": 0,
        "ram_gb": 0.0,
        "price_per_hour": price,
        "unit": unit,
        "category": category,
        "service": service,
        "region": region_lower,
        "details": details
    }


async def lookup_generic_aws_service(service: str, item_type: str, region: str = "us-east-1", cache: dict = None, cache_tasks: dict = None) -> dict:
    service_lower = service.lower()
    
    if service_lower == "iam":
        return {
            "instance_type": item_type or "IAM User/Role/Policy",
            "vcpus": 0,
            "ram_gb": 0.0,
            "price_per_hour": 0.0,
            "unit": "Hrs",
            "category": "security",
            "service": "iam",
            "region": region,
            "details": "IAM identity management is free of charge"
        }
        
    offer_code = SERVICE_OFFER_CODES.get(service_lower)
    if not offer_code:
        return get_generic_fallback_pricing(service_lower, item_type, region)
        
    url = f"https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{offer_code}/current/{region}/index.json"
    
    data = None
    if cache is not None and url in cache:
        data = cache[url]
    elif cache_tasks is not None and url in cache_tasks:
        data = await cache_tasks[url]
    else:
        logger.info(f"Looking up '{item_type}' under '{offer_code}' for region '{region}'...")
        try:
            if cache_tasks is not None:
                async def fetch_and_cache():
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        res = await client.get(url)
                        res.raise_for_status()
                        d = res.json()
                        if cache is not None:
                            cache[url] = d
                        return d
                task = asyncio.create_task(fetch_and_cache())
                cache_tasks[url] = task
                data = await task
            else:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    res = await client.get(url)
                    res.raise_for_status()
                    data = res.json()
                    if cache is not None:
                        cache[url] = data
        except Exception as e:
            logger.warning(f"AWS lookup failed for {service} ({offer_code}), using fallback: {e}")
            return get_generic_fallback_pricing(service_lower, item_type, region)
        
    products = data.get("products", {})
    terms = data.get("terms", {}).get("OnDemand", {})
    
    best_price = float("inf")
    best_match = None
    
    for sku, product in products.items():
        attrs = product.get("attributes", {})
        
        match = False
        if service_lower == "s3":
            if item_type.lower() in attrs.get("volumeType", "").lower() or item_type.lower() in attrs.get("storageClass", "").lower():
                match = True
            elif item_type.lower() in attrs.get("usagetype", "").lower():
                match = True
        elif service_lower == "ebs":
            if item_type.lower() in attrs.get("volumeApiName", "").lower() or item_type.lower() in attrs.get("volumeType", "").lower():
                match = True
        elif service_lower == "efs":
            if item_type.lower() in attrs.get("storageClass", "").lower():
                match = True
        elif service_lower in ["route53", "route 53"]:
            if item_type.lower() in attrs.get("usagetype", "").lower() or item_type.lower() in attrs.get("servicecode", "").lower():
                match = True
        elif service_lower == "vpc":
            if item_type.lower() in attrs.get("usagetype", "").lower() or item_type.lower() in attrs.get("operation", "").lower():
                match = True
        else:
            attr_vals = [str(v).lower() for v in attrs.values()]
            if any(item_type.lower() in v for v in attr_vals):
                match = True
                
        if not match:
            continue
            
        sku_terms = terms.get(sku, {})
        price = 0.0
        unit = "Hrs"
        for term_id, term_details in sku_terms.items():
            for rate_code, rate_details in term_details.get("priceDimensions", {}).items():
                price_str = rate_details.get("pricePerUnit", {}).get("USD", "0.0")
                price = float(price_str)
                unit = rate_details.get("unit", "Hrs")
                break
                
        if price <= 0.0:
            continue
            
        if price < best_price:
            best_price = price
            
            category = "general"
            if service_lower in ["s3", "ebs", "efs", "ecr"]:
                category = "storage"
            elif service_lower in ["vpc", "route53", "route 53", "cloudfront"]:
                category = "networking"
            elif service_lower in ["eks", "ecs"]:
                category = "compute"
            elif service_lower in ["waf", "iam"]:
                category = "security"
            elif service_lower in ["cloudwatch", "cloudtrail"]:
                category = "monitoring"
                
            best_match = {
                "instance_type": item_type,
                "vcpus": 0,
                "ram_gb": 0.0,
                "price_per_hour": price,
                "unit": unit,
                "category": category,
                "service": service_lower,
                "region": region,
                "details": f"Dynamically matched product sku: {sku}"
            }
            
    if not best_match:
        return get_generic_fallback_pricing(service_lower, item_type, region)
        
    return best_match
