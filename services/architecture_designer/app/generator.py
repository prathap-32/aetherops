# services/architecture_generator/app/generator.py
from typing import List
from app.schemas import (
    RequirementProfileOutput,
    ReactFlowGraphJSON,
    ReactFlowNode,
    ReactFlowNodeData,
    ReactFlowNodePosition,
    ReactFlowEdge
)

def generate_architecture_graph(profile: RequirementProfileOutput) -> ReactFlowGraphJSON:
    """
    Deterministic DAG Generator that maps architecture recommendations into a structured React Flow layout.
    """
    nodes: List[ReactFlowNode] = []
    edges: List[ReactFlowEdge] = []
    
    comp = profile.components
    ha_mode = profile.high_availability_mode
    is_multi_az = ha_mode in ["multi-az", "multi-region"]

    # 1. External Assets (Internet, CloudFront, S3)
    nodes.append(ReactFlowNode(
        id="internet",
        type="customNode",
        data=ReactFlowNodeData(
            label="Internet / Client",
            resource_type="internet",
            details={"description": "Public client traffic ingress/egress"}
        ),
        position=ReactFlowNodePosition(x=380, y=20)
    ))

    if comp.networking.has_cloudfront:
        nodes.append(ReactFlowNode(
            id="cloudfront",
            type="customNode",
            data=ReactFlowNodeData(
                label="Amazon CloudFront",
                resource_type="cloudfront",
                details={
                    "description": "Global Content Delivery Network",
                    "cost": f"${comp.networking.monthly_cost / 5:.2f}/mo (est)"
                }
            ),
            position=ReactFlowNodePosition(x=380, y=120)
        ))
        edges.append(ReactFlowEdge(
            id="edge-internet-cf",
            source="internet",
            target="cloudfront",
            animated=True,
            label="HTTPS Traffic"
        ))

    if comp.storage.s3_gb > 0:
        nodes.append(ReactFlowNode(
            id="s3-bucket",
            type="customNode",
            data=ReactFlowNodeData(
                label=f"Amazon S3 ({comp.storage.s3_class})",
                resource_type="s3",
                details={
                    "capacity": f"{comp.storage.s3_gb} GB",
                    "encryption": "SSE-KMS Enabled",
                    "cost": f"${comp.storage.monthly_cost:.2f}/mo"
                }
            ),
            position=ReactFlowNodePosition(x=900, y=360)
        ))

    # 2. VPC Group Container Node
    vpc_width = 820 if is_multi_az else 420
    vpc_height = 500
    
    nodes.append(ReactFlowNode(
        id="vpc-1",
        type="group",
        data=ReactFlowNodeData(
            label=f"AWS VPC (10.0.0.0/16) - {profile.architecture_tier} Tier",
            resource_type="vpc",
            details={
                "high_availability": ha_mode.upper(),
                "compliance": ", ".join(profile.compliance_applied) if profile.compliance_applied else "None"
            }
        ),
        position=ReactFlowNodePosition(x=40, y=220),
        width=float(vpc_width),
        height=float(vpc_height)
    ))

    # AZ-A Subnets
    nodes.append(ReactFlowNode(
        id="subnet-public-a",
        type="group",
        parentId="vpc-1",
        data=ReactFlowNodeData(label="Public Subnet AZ-A (10.0.1.0/24)", resource_type="subnet"),
        position=ReactFlowNodePosition(x=40, y=60),
        width=340.0,
        height=160.0
    ))
    
    nodes.append(ReactFlowNode(
        id="subnet-private-a",
        type="group",
        parentId="vpc-1",
        data=ReactFlowNodeData(label="Private Subnet AZ-A (10.0.2.0/24)", resource_type="subnet"),
        position=ReactFlowNodePosition(x=40, y=260),
        width=340.0,
        height=200.0
    ))

    # Load Balancer (ALB)
    if comp.networking.has_alb:
        nodes.append(ReactFlowNode(
            id="alb-1",
            type="customNode",
            parentId="subnet-public-a",
            data=ReactFlowNodeData(
                label="Application Load Balancer",
                resource_type="alb",
                details={
                    "scheme": "internet-facing",
                    "waf_integrated": str(comp.security.waf_enabled)
                }
            ),
            position=ReactFlowNodePosition(x=30, y=40)
        ))
        
        source_node = "cloudfront" if comp.networking.has_cloudfront else "internet"
        edges.append(ReactFlowEdge(
            id="edge-ingress-alb",
            source=source_node,
            target="alb-1",
            animated=True,
            label="HTTP/HTTPS"
        ))

    # NAT Gateway in Public Subnet A
    if comp.networking.nat_gateway_count >= 1:
        nodes.append(ReactFlowNode(
            id="nat-gw-a",
            type="customNode",
            parentId="subnet-public-a",
            data=ReactFlowNodeData(
                label="NAT Gateway AZ-A",
                resource_type="nat",
                details={"ip": "Elastic IP (Static)"}
            ),
            position=ReactFlowNodePosition(x=200, y=40)
        ))
        edges.append(ReactFlowEdge(
            id="edge-nat-gw-egress",
            source="nat-gw-a",
            target="internet",
            animated=False,
            label="Egress Routing"
        ))

    # Compute Instance in Private Subnet A
    nodes.append(ReactFlowNode(
        id="ec2-a",
        type="customNode",
        parentId="subnet-private-a",
        data=ReactFlowNodeData(
            label=f"EC2 Instance ({comp.compute.instance_type})",
            resource_type="ec2",
            details={
                "vcpus": f"{comp.compute.vcpus} vCPU",
                "ram": f"{comp.compute.ram_gb} GB RAM",
                "ebs_storage": f"{comp.storage.ebs_gb_per_instance} GB gp3",
                "autoscaling": "ASG Active" if comp.compute.has_autoscaling else "Single Instance"
            }
        ),
        position=ReactFlowNodePosition(x=30, y=45)
    ))

    if comp.networking.has_alb:
        edges.append(ReactFlowEdge(
            id="edge-alb-ec2a",
            source="alb-1",
            target="ec2-a",
            animated=True
        ))
    else:
        edges.append(ReactFlowEdge(
            id="edge-direct-ec2a",
            source="internet",
            target="ec2-a",
            animated=True
        ))

    # Database Master in Private Subnet A
    nodes.append(ReactFlowNode(
        id="rds-master",
        type="customNode",
        parentId="subnet-private-a",
        data=ReactFlowNodeData(
            label=f"RDS Master ({comp.database.instance_type})",
            resource_type="rds",
            details={
                "engine": "PostgreSQL / MySQL",
                "storage": f"{comp.database.storage_gb} GB gp3",
                "role": "Master Write/Read"
            }
        ),
        position=ReactFlowNodePosition(x=190, y=45)
    ))

    edges.append(ReactFlowEdge(
        id="edge-ec2a-rds",
        source="ec2-a",
        target="rds-master",
        animated=False,
        label="SQL Queries"
    ))

    if comp.networking.nat_gateway_count >= 1:
        edges.append(ReactFlowEdge(
            id="edge-ec2a-natgw",
            source="ec2-a",
            target="nat-gw-a",
            animated=False,
            label="Internet Access"
        ))

    if comp.storage.s3_gb > 0:
        edges.append(ReactFlowEdge(
            id="edge-rds-s3",
            source="rds-master",
            target="s3-bucket",
            animated=False,
            label="Backup Upload",
            style={"strokeDasharray": "5,5"}
        ))

    # AZ-B Subnets (if Multi-AZ)
    if is_multi_az:
        nodes.append(ReactFlowNode(
            id="subnet-public-b",
            type="group",
            parentId="vpc-1",
            data=ReactFlowNodeData(label="Public Subnet AZ-B (10.0.3.0/24)", resource_type="subnet"),
            position=ReactFlowNodePosition(x=440, y=60),
            width=340.0,
            height=160.0
        ))

        nodes.append(ReactFlowNode(
            id="subnet-private-b",
            type="group",
            parentId="vpc-1",
            data=ReactFlowNodeData(label="Private Subnet AZ-B (10.0.4.0/24)", resource_type="subnet"),
            position=ReactFlowNodePosition(x=440, y=260),
            width=340.0,
            height=200.0
        ))

        if comp.networking.nat_gateway_count >= 2:
            nodes.append(ReactFlowNode(
                id="nat-gw-b",
                type="customNode",
                parentId="subnet-public-b",
                data=ReactFlowNodeData(
                    label="NAT Gateway AZ-B",
                    resource_type="nat",
                    details={"ip": "Elastic IP (Static)"}
                ),
                position=ReactFlowNodePosition(x=200, y=40)
            ))
            edges.append(ReactFlowEdge(
                id="edge-nat-gw-b-egress",
                source="nat-gw-b",
                target="internet",
                animated=False,
                label="Egress Routing"
            ))

        nodes.append(ReactFlowNode(
            id="ec2-b",
            type="customNode",
            parentId="subnet-private-b",
            data=ReactFlowNodeData(
                label=f"EC2 Instance ({comp.compute.instance_type})",
                resource_type="ec2",
                details={
                    "vcpus": f"{comp.compute.vcpus} vCPU",
                    "ram": f"{comp.compute.ram_gb} GB RAM",
                    "ebs_storage": f"{comp.storage.ebs_gb_per_instance} GB gp3",
                    "autoscaling": "ASG Active"
                }
            ),
            position=ReactFlowNodePosition(x=30, y=45)
        ))

        if comp.networking.has_alb:
            edges.append(ReactFlowEdge(
                id="edge-alb-ec2b",
                source="alb-1",
                target="ec2-b",
                animated=True
            ))

        nodes.append(ReactFlowNode(
            id="rds-replica",
            type="customNode",
            parentId="subnet-private-b",
            data=ReactFlowNodeData(
                label=f"RDS Standby ({comp.database.instance_type})",
                resource_type="rds",
                details={
                    "engine": "PostgreSQL / MySQL",
                    "storage": f"{comp.database.storage_gb} GB gp3",
                    "role": "Standby Replica (Read-Only)"
                }
            ),
            position=ReactFlowNodePosition(x=190, y=45)
        ))

        edges.append(ReactFlowEdge(
            id="edge-ec2b-rds-replica",
            source="ec2-b",
            target="rds-replica",
            animated=False,
            label="Reads Only"
        ))

        edges.append(ReactFlowEdge(
            id="edge-db-replication",
            source="rds-master",
            target="rds-replica",
            animated=True,
            label="Sync Replication",
            style={"strokeDasharray": "4,4", "stroke": "#10B981"}
        ))

        nat_gw_target = "nat-gw-b" if comp.networking.nat_gateway_count >= 2 else "nat-gw-a"
        if comp.networking.nat_gateway_count >= 1:
            edges.append(ReactFlowEdge(
                id="edge-ec2b-natgw",
                source="ec2-b",
                target=nat_gw_target,
                animated=False,
                label="Internet Access"
            ))

    return ReactFlowGraphJSON(nodes=nodes, edges=edges)
