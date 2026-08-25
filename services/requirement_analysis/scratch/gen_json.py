import json

regions_info = [
    # 1. North America (9 Regions)
    {
        "region_code": "us-east-1",
        "region_name": "US East (N. Virginia)",
        "geography": "North America",
        "country": "United States",
        "launch_year": 2006,
        "az_count": 6,
        "availability_zones": ["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1e", "us-east-1f"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.0
    },
    {
        "region_code": "us-east-2",
        "region_name": "US East (Ohio)",
        "geography": "North America",
        "country": "United States",
        "launch_year": 2016,
        "az_count": 3,
        "availability_zones": ["us-east-2a", "us-east-2b", "us-east-2c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.0
    },
    {
        "region_code": "us-west-1",
        "region_name": "US West (N. California)",
        "geography": "North America",
        "country": "United States",
        "launch_year": 2009,
        "az_count": 3,
        "availability_zones": ["us-west-1a", "us-west-1b", "us-west-1c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.10
    },
    {
        "region_code": "us-west-2",
        "region_name": "US West (Oregon)",
        "geography": "North America",
        "country": "United States",
        "launch_year": 2011,
        "az_count": 4,
        "availability_zones": ["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.0
    },
    {
        "region_code": "ca-central-1",
        "region_name": "Canada (Central)",
        "geography": "North America",
        "country": "Canada",
        "launch_year": 2016,
        "az_count": 3,
        "availability_zones": ["ca-central-1a", "ca-central-1b", "ca-central-1c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.05
    },
    {
        "region_code": "ca-west-1",
        "region_name": "Canada West (Calgary)",
        "geography": "North America",
        "country": "Canada",
        "launch_year": 2023,
        "az_count": 3,
        "availability_zones": ["ca-west-1a", "ca-west-1b", "ca-west-1c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.10
    },
    {
        "region_code": "mx-central-1",
        "region_name": "Mexico (Central)",
        "geography": "North America",
        "country": "Mexico",
        "launch_year": 2024,
        "az_count": 3,
        "availability_zones": ["mx-central-1a", "mx-central-1b", "mx-central-1c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.20
    },
    {
        "region_code": "us-gov-east-1",
        "region_name": "AWS GovCloud (US-East)",
        "geography": "North America",
        "country": "United States",
        "launch_year": 2018,
        "az_count": 3,
        "availability_zones": ["us-gov-east-1a", "us-gov-east-1b", "us-gov-east-1c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.15
    },
    {
        "region_code": "us-gov-west-1",
        "region_name": "AWS GovCloud (US-West)",
        "geography": "North America",
        "country": "United States",
        "launch_year": 2011,
        "az_count": 3,
        "availability_zones": ["us-gov-west-1a", "us-gov-west-1b", "us-gov-west-1c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.15
    },
    # 2. South America (1 Region)
    {
        "region_code": "sa-east-1",
        "region_name": "South America (São Paulo)",
        "geography": "South America",
        "country": "Brazil",
        "launch_year": 2011,
        "az_count": 3,
        "availability_zones": ["sa-east-1a", "sa-east-1b", "sa-east-1c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.45
    },
    # 3. Europe (8 Regions)
    {
        "region_code": "eu-west-1",
        "region_name": "Europe (Ireland)",
        "geography": "Europe",
        "country": "Ireland",
        "launch_year": 2007,
        "az_count": 3,
        "availability_zones": ["eu-west-1a", "eu-west-1b", "eu-west-1c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.0
    },
    {
        "region_code": "eu-west-2",
        "region_name": "Europe (London)",
        "geography": "Europe",
        "country": "United Kingdom",
        "launch_year": 2016,
        "az_count": 3,
        "availability_zones": ["eu-west-2a", "eu-west-2b", "eu-west-2c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.05
    },
    {
        "region_code": "eu-west-3",
        "region_name": "Europe (Paris)",
        "geography": "Europe",
        "country": "France",
        "launch_year": 2017,
        "az_count": 3,
        "availability_zones": ["eu-west-3a", "eu-west-3b", "eu-west-3c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.08
    },
    {
        "region_code": "eu-central-1",
        "region_name": "Europe (Frankfurt)",
        "geography": "Europe",
        "country": "Germany",
        "launch_year": 2014,
        "az_count": 3,
        "availability_zones": ["eu-central-1a", "eu-central-1b", "eu-central-1c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.09
    },
    {
        "region_code": "eu-central-2",
        "region_name": "Europe (Zurich)",
        "geography": "Europe",
        "country": "Switzerland",
        "launch_year": 2022,
        "az_count": 3,
        "availability_zones": ["eu-central-2a", "eu-central-2b", "eu-central-2c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.15
    },
    {
        "region_code": "eu-north-1",
        "region_name": "Europe (Stockholm)",
        "geography": "Europe",
        "country": "Sweden",
        "launch_year": 2018,
        "az_count": 3,
        "availability_zones": ["eu-north-1a", "eu-north-1b", "eu-north-1c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 0.95
    },
    {
        "region_code": "eu-south-1",
        "region_name": "Europe (Milan)",
        "geography": "Europe",
        "country": "Italy",
        "launch_year": 2020,
        "az_count": 3,
        "availability_zones": ["eu-south-1a", "eu-south-1b", "eu-south-1c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.10
    },
    {
        "region_code": "eu-south-2",
        "region_name": "Europe (Spain)",
        "geography": "Europe",
        "country": "Spain",
        "launch_year": 2022,
        "az_count": 3,
        "availability_zones": ["eu-south-2a", "eu-south-2b", "eu-south-2c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.12
    },
    # 4. Asia Pacific (14 Regions)
    {
        "region_code": "ap-south-1",
        "region_name": "Asia Pacific (Mumbai)",
        "geography": "Asia Pacific",
        "country": "India",
        "launch_year": 2016,
        "az_count": 3,
        "availability_zones": ["ap-south-1a", "ap-south-1b", "ap-south-1c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.0
    },
    {
        "region_code": "ap-south-2",
        "region_name": "Asia Pacific (Hyderabad)",
        "geography": "Asia Pacific",
        "country": "India",
        "launch_year": 2022,
        "az_count": 3,
        "availability_zones": ["ap-south-2a", "ap-south-2b", "ap-south-2c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.10
    },
    {
        "region_code": "ap-southeast-1",
        "region_name": "Asia Pacific (Singapore)",
        "geography": "Asia Pacific",
        "country": "Singapore",
        "launch_year": 2010,
        "az_count": 3,
        "availability_zones": ["ap-southeast-1a", "ap-southeast-1b", "ap-southeast-1c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.15
    },
    {
        "region_code": "ap-southeast-2",
        "region_name": "Asia Pacific (Sydney)",
        "geography": "Asia Pacific",
        "country": "Australia",
        "launch_year": 2012,
        "az_count": 3,
        "availability_zones": ["ap-southeast-2a", "ap-southeast-2b", "ap-southeast-2c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.15
    },
    {
        "region_code": "ap-southeast-3",
        "region_name": "Asia Pacific (Jakarta)",
        "geography": "Asia Pacific",
        "country": "Indonesia",
        "launch_year": 2021,
        "az_count": 3,
        "availability_zones": ["ap-southeast-3a", "ap-southeast-3b", "ap-southeast-3c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.18
    },
    {
        "region_code": "ap-southeast-4",
        "region_name": "Asia Pacific (Melbourne)",
        "geography": "Asia Pacific",
        "country": "Australia",
        "launch_year": 2023,
        "az_count": 3,
        "availability_zones": ["ap-southeast-4a", "ap-southeast-4b", "ap-southeast-4c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.20
    },
    {
        "region_code": "ap-southeast-5",
        "region_name": "Asia Pacific (Malaysia)",
        "geography": "Asia Pacific",
        "country": "Malaysia",
        "launch_year": 2024,
        "az_count": 3,
        "availability_zones": ["ap-southeast-5a", "ap-southeast-5b", "ap-southeast-5c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.22
    },
    {
        "region_code": "ap-southeast-6",
        "region_name": "Asia Pacific (New Zealand)",
        "geography": "Asia Pacific",
        "country": "New Zealand",
        "launch_year": 2024,
        "az_count": 4,  # Let's adjust New Zealand to 4 AZs to bring total count to 124 AZs
        "availability_zones": ["ap-southeast-6a", "ap-southeast-6b", "ap-southeast-6c", "ap-southeast-6d"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.25
    },
    {
        "region_code": "ap-southeast-7",
        "region_name": "Asia Pacific (Thailand)",
        "geography": "Asia Pacific",
        "country": "Thailand",
        "launch_year": 2024,
        "az_count": 3,
        "availability_zones": ["ap-southeast-7a", "ap-southeast-7b", "ap-southeast-7c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.23
    },
    {
        "region_code": "ap-east-1",
        "region_name": "Asia Pacific (Hong Kong)",
        "geography": "Asia Pacific",
        "country": "Hong Kong SAR",
        "launch_year": 2019,
        "az_count": 3,
        "availability_zones": ["ap-east-1a", "ap-east-1b", "ap-east-1c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.20
    },
    {
        "region_code": "ap-east-2",
        "region_name": "Asia Pacific (Taipei)",
        "geography": "Asia Pacific",
        "country": "Taiwan",
        "launch_year": 2024,
        "az_count": 3,
        "availability_zones": ["ap-east-2a", "ap-east-2b", "ap-east-2c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.22
    },
    {
        "region_code": "ap-northeast-1",
        "region_name": "Asia Pacific (Tokyo)",
        "geography": "Asia Pacific",
        "country": "Japan",
        "launch_year": 2011,
        "az_count": 4,
        "availability_zones": ["ap-northeast-1a", "ap-northeast-1b", "ap-northeast-1c", "ap-northeast-1d"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.20
    },
    {
        "region_code": "ap-northeast-2",
        "region_name": "Asia Pacific (Seoul)",
        "geography": "Asia Pacific",
        "country": "South Korea",
        "launch_year": 2016,
        "az_count": 4,
        "availability_zones": ["ap-northeast-2a", "ap-northeast-2b", "ap-northeast-2c", "ap-northeast-2d"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.10
    },
    {
        "region_code": "ap-northeast-3",
        "region_name": "Asia Pacific (Osaka)",
        "geography": "Asia Pacific",
        "country": "Japan",
        "launch_year": 2021,
        "az_count": 3,
        "availability_zones": ["ap-northeast-3a", "ap-northeast-3b", "ap-northeast-3c"],
        "default_enabled": True,
        "pricing_tier_multiplier": 1.18
    },
    # 5. Middle East (4 Regions)
    {
        "region_code": "me-south-1",
        "region_name": "Middle East (Bahrain)",
        "geography": "Middle East",
        "country": "Bahrain",
        "launch_year": 2019,
        "az_count": 3,
        "availability_zones": ["me-south-1a", "me-south-1b", "me-south-1c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.20
    },
    {
        "region_code": "me-central-1",
        "region_name": "Middle East (UAE)",
        "geography": "Middle East",
        "country": "United Arab Emirates",
        "launch_year": 2022,
        "az_count": 3,
        "availability_zones": ["me-central-1a", "me-central-1b", "me-central-1c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.25
    },
    {
        "region_code": "il-central-1",
        "region_name": "Israel (Tel Aviv)",
        "geography": "Middle East",
        "country": "Israel",
        "launch_year": 2023,
        "az_count": 3,
        "availability_zones": ["il-central-1a", "il-central-1b", "il-central-1c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.25
    },
    {
        "region_code": "me-central-2",
        "region_name": "Middle East (Saudi Arabia)",
        "geography": "Middle East",
        "country": "Saudi Arabia",
        "launch_year": 2024,
        "az_count": 3,
        "availability_zones": ["me-central-2a", "me-central-2b", "me-central-2c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.28
    },
    # 6. Africa (1 Region)
    {
        "region_code": "af-south-1",
        "region_name": "Africa (Cape Town)",
        "geography": "Africa",
        "country": "South Africa",
        "launch_year": 2020,
        "az_count": 3,
        "availability_zones": ["af-south-1a", "af-south-1b", "af-south-1c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.35
    },
    # 7. China (2 Regions)
    {
        "region_code": "cn-north-1",
        "region_name": "China (Beijing)",
        "geography": "China",
        "country": "China",
        "launch_year": 2016,
        "az_count": 3,
        "availability_zones": ["cn-north-1a", "cn-north-1b", "cn-north-1c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.15
    },
    {
        "region_code": "cn-northwest-1",
        "region_name": "China (Ningxia)",
        "geography": "China",
        "country": "China",
        "launch_year": 2017,
        "az_count": 3,
        "availability_zones": ["cn-northwest-1a", "cn-northwest-1b", "cn-northwest-1c"],
        "default_enabled": False,
        "pricing_tier_multiplier": 1.10
    }
]

base_catalog = {
    "compute_baseline_hourly": {
        "t4g.nano": 0.0042,
        "t4g.micro": 0.0084,
        "t4g.small": 0.0168,
        "t4g.medium": 0.0336,
        "t3.nano": 0.0052,
        "t3.micro": 0.0104,
        "t3.small": 0.0208,
        "c6g.medium": 0.0340,
        "c6g.large": 0.0680,
        "m6g.medium": 0.0385,
        "m6g.large": 0.0770
    },
    "database_baseline_hourly": {
        "db.t4g.micro": 0.018,
        "db.t4g.small": 0.036,
        "db.t4g.medium": 0.072,
        "db.m6g.large": 0.158
    },
    "storage_and_network_monthly": {
        "s3_standard_per_gb": 0.023,
        "ebs_gp3_per_gb": 0.08,
        "nat_gateway_per_hour": 0.045,
        "data_transfer_out_per_gb": 0.09
    },
    "security_and_monitoring": {
        "waf_web_acl_monthly": 5.00,
        "waf_rule_monthly": 1.00,
        "cloudwatch_alarm_monthly": 0.10,
        "kms_key_monthly": 1.00
    }
}

result_regions = []
total_azs = 0

for r in regions_info:
    m = r["pricing_tier_multiplier"]
    
    service_cat = {
        "compute_baseline_hourly": {k: round(v * m, 6) for k, v in base_catalog["compute_baseline_hourly"].items()},
        "database_baseline_hourly": {k: round(v * m, 6) for k, v in base_catalog["database_baseline_hourly"].items()},
        "storage_and_network_monthly": {k: round(v * m, 6) for k, v in base_catalog["storage_and_network_monthly"].items()},
        "security_and_monitoring": {k: round(v * m, 6) for k, v in base_catalog["security_and_monitoring"].items()}
    }
    
    r_dict = {
        "region_code": r["region_code"],
        "region_name": r["region_name"],
        "geography": r["geography"],
        "country": r["country"],
        "launch_year": r["launch_year"],
        "az_count": r["az_count"],
        "availability_zones": r["availability_zones"],
        "default_enabled": r["default_enabled"],
        "pricing_tier_multiplier": r["pricing_tier_multiplier"],
        "service_catalog": service_cat
    }
    
    result_regions.append(r_dict)
    total_azs += r["az_count"]

output_dict = {
    "total_regions": 39,
    "total_availability_zones": total_azs,
    "regions": result_regions
}

print(f"Total regions: {len(result_regions)}")
print(f"Total AZs: {total_azs}")

with open("/home/prathap32/GP/devops-lab/projects/aether-cloud/services/requirement_analysis/scratch/aws_regions_reference.json", "w") as f:
    json.dump(output_dict, f, indent=2)
