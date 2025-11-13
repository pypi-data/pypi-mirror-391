"""
Object counting functionality for educational content evaluation.

This module provides bias-free object counting using Claude's vision capabilities.
The counting is done without knowledge of expected content to avoid anchoring bias.
"""

import asyncio
import base64
import logging
import os
from typing import List, Optional

import requests
from anthropic import AsyncAnthropic
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GroupCount(BaseModel):
    """Count data for a specific group within grouped objects."""
    group_identifier: str  # e.g., "Blue row", "Basket 1", "Left plate"
    count: float  # Whole numbers or 0.5 increments


class ObjectTypeCount(BaseModel):
    """Count data for a specific object type."""
    object_name: str
    scenario_classification: str  # scattered, grouped, clustered, mixed
    counting_strategy_used: str
    method_1_count: float
    method_1_details: str
    method_2_count: float
    method_2_details: str
    method_3_count: float
    method_3_details: str
    method_agreement: str
    sanity_check: str
    quality_assessment: str
    confidence_level: str  # high, medium, low
    final_verified_count: float
    count_discrepancies: Optional[str] = None
    container_relationship: Optional[str] = None
    group_breakdown: Optional[List[GroupCount]] = None


class ImageCountData(BaseModel):
    """Object count data for a single image."""
    image_url: str
    image_index: int
    overall_confidence: str  # high, medium, low
    image_rejected: bool
    rejection_reason: Optional[str] = None
    counting_process_summary: str
    object_types: List[ObjectTypeCount]


class ObjectCountResult(BaseModel):
    """Result from counting objects in one or more images."""
    success: bool
    image_counts: List[ImageCountData]
    error_message: Optional[str] = None


async def count_objects_in_images(image_urls: List[str]) -> ObjectCountResult:
    """
    Count objects in images without any bias from expected descriptions.
    
    Uses Claude's vision capabilities with a multi-method verification approach
    to ensure accurate counting. Adapts counting strategy based on image content.
    
    Parameters
    ----------
    image_urls : List[str]
        List of image URLs to analyze for object counting
        
    Returns
    -------
    ObjectCountResult
        Structured count data including counts per object type, confidence levels,
        and detailed verification information
    """
    if not image_urls:
        return ObjectCountResult(
            success=True,
            image_counts=[],
            error_message=None
        )
    
    try:
        client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY_COUNTING'))
        
        system_prompt = """You are an expert at precise object counting in images. You will use a
systematic, adaptive approach that works for any counting scenario.

CRITICAL: You will receive NO information about expected counts. Count only what you observe.

## Universal Counting Strategy

**STEP 1 - SCENE ANALYSIS:**
- Analyze the image to understand the counting challenge
- Classify the scenario:
  * SCATTERED: Individual objects distributed across the image
  * GROUPED: Objects organized in containers/groups (plates, bowls, baskets, etc.)
  * CLUSTERED: Objects touching/overlapping but not in containers
  * MIXED: Multiple object types or complex arrangements
- Identify all distinct object types present
- **DETERMINE IMAGE TYPE**: Is this a chart/graph/diagram OR a realistic scene?

**STEP 2 - ADAPTIVE COUNTING APPROACH:**

For SCATTERED objects:
- Use systematic grid scanning (divide image into regions)
- Count each object type separately
- Mark objects mentally as you count to avoid double-counting

For GROUPED objects:
- Count containers first, then contents of each container
- **CRITICAL**: Record per-group counts individually with clear identifiers
  (e.g., "Blue row: 2.5", "Red row: 3.5", "Green row: 4.0")
- Check if groups are consistent (same count per group)
- Provide structured breakdown of each group's count

For CLUSTERED objects:
- Use edge detection and separation techniques mentally
- Count visible objects only (>80% visible)
- Be extra careful with touching/overlapping objects

For MIXED scenarios:
- Count each object type independently
- Use color, shape, size differences to distinguish types
- Double-check boundaries between different object types

**STEP 3 - MULTI-METHOD VERIFICATION:**
- **Method 1**: Use your primary systematic approach based on scenario
- **Method 2**: Use an alternative counting method appropriate to the scenario
- **Method 3**: Verify using a third independent approach
- **Cross-verify**: All methods should agree within 1-2 objects

## Critical Counting Rules

- **PARTIAL OBJECTS IN EDUCATIONAL IMAGES**: 
  * In charts/graphs/pictographs: Partial symbols ARE meaningful and should be counted as 0.5
    Example: A pictograph showing "2.5 oranges" uses half-symbols intentionally
  * In realistic scenes: Partial objects usually represent WHOLE objects that are occluded
    Example: An apple half-hidden behind another apple should count as 1, not 0.5
  * ONLY use 0.5 increments - never be more precise (no 0.3, 0.7, etc.)
  * When uncertain, default to whole number counts

- **VISIBILITY RULE**: 
  * Charts/graphs: Count all visible symbols including partial ones
    (count as 0.5 if approximately half)
  * Realistic scenes: Only count objects >80% visible as whole objects

- **EDGE POLICY**: 
  * Charts/graphs: Objects cut at edge likely represent partial quantities (count as 0.5)
  * Realistic scenes: Objects cut off by boundaries typically don't count

- **OCCLUSION HANDLING**: If objects are heavily overlapped/ambiguous → REJECT image
- **EDUCATIONAL SUITABILITY**: If a student couldn't clearly count these objects → REJECT
- **PRECISION REQUIREMENT**: Be exact - use whole numbers OR .5 increments only
- **CONTEXT CLUES**: Use visual cues (stems, handles, outlines) to distinguish objects

## Quality Control Checks

1. **Sanity Check**: Does the total make sense given the image size and object density?
2. **Method Agreement**: Do all counting methods agree within acceptable range?
3. **Confidence Assessment**: How clear and unambiguous are the objects?
4. **Student Suitability**: Could a grade-level student count these objects clearly?

## Output Requirements

For each object type found:
1. **Scenario Classification**: What type of counting challenge is this?
2. **Counting Strategy Used**: Which approach was most appropriate?
3. **Group Breakdown** (REQUIRED for "grouped" scenarios): Provide a structured list of each
   group with its identifier and count
   - Example: [{"group_identifier": "Blue row", "count": 2.5}, 
               {"group_identifier": "Red row", "count": 3.5}]
   - Use clear, descriptive identifiers
   - This allows the evaluator to verify counts match expected group structure
4. **Method Results**: Results from each verification method with details
5. **Final Count**: Verified count after cross-checking (should equal sum of group counts)
   - Use whole numbers OR .5 increments ONLY (e.g., 3, 3.5, 4 - never 3.3 or 3.7)
   - In charts/pictographs: Count partial symbols as 0.5
   - In realistic scenes: Count occluded objects as whole numbers (1.0)
6. **Confidence Level**: HIGH (objects clearly distinct, well-lit, unobscured, easy to count),
   MEDIUM (some overlap or shadows but still countable), or LOW (difficult to distinguish,
   heavily overlapping, or ambiguous)
7. **Quality Assessment**: Whether image is suitable for educational counting

You must be absolutely certain of your final counts. When in doubt, examine more carefully and be
conservative."""

        # Prepare message content
        if len(image_urls) == 1:
            message_text = """Please carefully count all distinct objects in this image using the
universal counting strategy. Be systematic and thorough.

IMPORTANT STEPS:
1. ANALYZE the image first:
   - What type of counting scenario is this? (scattered, grouped, clustered, mixed)
   - Is this a chart/graph/pictograph OR a realistic scene?
   - Are there any PARTIAL objects visible (half-symbols in charts, or objects at edges)?
   - If GROUPED: What are the distinct groups? (e.g., rows, baskets, plates)
2. CHOOSE the most appropriate counting approach for this specific scenario
3. COUNT using your chosen method, being precise and systematic
   - For charts/graphs: Count partial symbols as 0.5 (e.g., 3.5 grapes)
   - For realistic scenes: Count occluded objects as whole numbers
   - Use ONLY whole numbers or .5 increments
   - If GROUPED: Count each group separately and record with clear identifiers
4. VERIFY using alternative methods appropriate to the scenario
5. CROSS-CHECK that all methods agree within acceptable range
6. If GROUPED: Provide group_breakdown with each group's identifier and count

REJECT if objects are overlapping, ambiguous, or impossible for students to count clearly."""
        else:
            message_text = f"""Please carefully count all distinct objects in each of these
{len(image_urls)} images using the universal counting strategy. Provide separate counts for each
image.

IMPORTANT STEPS FOR EACH IMAGE:
1. ANALYZE the image first:
   - What type of counting scenario is this? (scattered, grouped, clustered, mixed)
   - Is this a chart/graph/pictograph OR a realistic scene?
   - Are there any PARTIAL objects visible (half-symbols in charts, or objects at edges)?
   - If GROUPED: What are the distinct groups? (e.g., rows, baskets, plates)
2. CHOOSE the most appropriate counting approach for this specific scenario
3. COUNT using your chosen method, being precise and systematic
   - For charts/graphs: Count partial symbols as 0.5 (e.g., 3.5 grapes)
   - For realistic scenes: Count occluded objects as whole numbers
   - Use ONLY whole numbers or .5 increments
   - If GROUPED: Count each group separately and record with clear identifiers
4. VERIFY using alternative methods appropriate to the scenario
5. CROSS-CHECK that all methods agree within acceptable range
6. If GROUPED: Provide group_breakdown with each group's identifier and count

REJECT if objects are overlapping, ambiguous, or impossible for students to count clearly."""
        
        message_content = [{"type": "text", "text": message_text}]
        
        # Add images to message
        for i, image_url in enumerate(image_urls):
            if len(image_urls) > 1:
                message_content.append({
                    "type": "text",
                    "text": f"=== IMAGE {i+1} (URL: {image_url}) ==="
                })
            
            # Try to download and encode as base64 for better reliability
            try:
                await asyncio.sleep(0.5)  # Small delay between requests
                image_response = requests.get(image_url, timeout=30)
                image_response.raise_for_status()
                image_bytes = image_response.content
                if image_bytes:
                    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                    content_type = image_response.headers.get('content-type', 'image/png')
                    media_type = "image/jpeg" if 'jpeg' in content_type or 'jpg' in content_type \
                        else "image/png"
                    
                    message_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64
                        }
                    })
                else:
                    # Fallback to URL
                    message_content.append({
                        "type": "image",
                        "source": {"type": "url", "url": image_url}
                    })
            except Exception as e:
                logger.warning(f"Error downloading image {i+1}, using URL: {e}")
                message_content.append({
                    "type": "image",
                    "source": {"type": "url", "url": image_url}
                })

        # Define structured output tool for object counting
        tools = [{
            "name": "object_count_report",
            "description": "Report detailed object counts for each image",
            "input_schema": {
                "type": "object",
                "properties": {
                    "image_counts": {
                        "type": "array",
                        "description": "Object counts for each image",
                        "items": {
                            "type": "object",
                            "properties": {
                                "image_url": {
                                    "type": "string",
                                    "description": "URL of the image being analyzed"
                                },
                                "image_index": {
                                    "type": "integer",
                                    "description": (
                                        "Index of image (1-based) in the provided sequence"
                                    )
                                },
                                "overall_confidence": {
                                    "type": "string",
                                    "enum": ["high", "medium", "low"],
                                    "description": (
                                        "Overall confidence level for this image's counts"
                                    )
                                },
                                "image_rejected": {
                                    "type": "boolean",
                                    "description": (
                                        "True if image should be rejected due to "
                                        "obscured/ambiguous objects"
                                    )
                                },
                                "rejection_reason": {
                                    "type": "string",
                                    "description": "Reason for rejection if image_rejected is true"
                                },
                                "counting_process_summary": {
                                    "type": "string",
                                    "description": (
                                        "Summary of the multi-method counting process used"
                                    )
                                },
                                "object_types": {
                                    "type": "array",
                                    "description": (
                                        "List of different object types found with counts"
                                    ),
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "object_name": {
                                                "type": "string",
                                                "description": (
                                                    "Name/type of object (e.g., 'baskets', "
                                                    "'apples')"
                                                )
                                            },
                                            "scenario_classification": {
                                                "type": "string",
                                                "enum": ["scattered", "grouped", "clustered",
                                                        "mixed"],
                                                "description": (
                                                    "Type of counting scenario identified"
                                                )
                                            },
                                            "counting_strategy_used": {
                                                "type": "string",
                                                "description": (
                                                    "Which counting approach was most appropriate "
                                                    "for this scenario"
                                                )
                                            },
                                            "method_1_count": {
                                                "type": "number",
                                                "description": (
                                                    "Count from first method (whole numbers or 0.5 "
                                                    "increments only)"
                                                )
                                            },
                                            "method_1_details": {
                                                "type": "string",
                                                "description": "Details from first counting method"
                                            },
                                            "method_2_count": {
                                                "type": "number",
                                                "description": (
                                                    "Count from second method (whole numbers or "
                                                    "0.5 increments only)"
                                                )
                                            },
                                            "method_2_details": {
                                                "type": "string",
                                                "description": "Details from second method"
                                            },
                                            "method_3_count": {
                                                "type": "number",
                                                "description": (
                                                    "Count from third method (whole numbers or "
                                                    "0.5 increments only)"
                                                )
                                            },
                                            "method_3_details": {
                                                "type": "string",
                                                "description": "Details from third method"
                                            },
                                            "method_agreement": {
                                                "type": "string",
                                                "description": (
                                                    "Analysis of agreement between different "
                                                    "counting methods"
                                                )
                                            },
                                            "sanity_check": {
                                                "type": "string",
                                                "description": (
                                                    "Assessment of whether the count makes sense "
                                                    "given image characteristics"
                                                )
                                            },
                                            "quality_assessment": {
                                                "type": "string",
                                                "description": (
                                                    "Whether image is suitable for educational "
                                                    "counting"
                                                )
                                            },
                                            "confidence_level": {
                                                "type": "string",
                                                "enum": ["high", "medium", "low"],
                                                "description": (
                                                    "Confidence level for this object type count"
                                                )
                                            },
                                            "final_verified_count": {
                                                "type": "number",
                                                "description": (
                                                    "Final verified count after resolving any "
                                                    "discrepancies (whole numbers or 0.5 "
                                                    "increments only)"
                                                )
                                            },
                                            "count_discrepancies": {
                                                "type": "string",
                                                "description": (
                                                    "Any discrepancies between methods and how "
                                                    "they were resolved"
                                                )
                                            },
                                            "container_relationship": {
                                                "type": "string",
                                                "description": (
                                                    "If objects are inside containers, describe "
                                                    "the relationship (e.g., 'apples inside "
                                                    "baskets')"
                                                )
                                            },
                                            "group_breakdown": {
                                                "type": "array",
                                                "description": (
                                                    "REQUIRED for grouped scenarios: List of "
                                                    "per-group counts with clear identifiers "
                                                    "(e.g., [{group_identifier: 'Blue row', "
                                                    "count: 2.5}, ...])"
                                                ),
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "group_identifier": {
                                                            "type": "string",
                                                            "description": (
                                                                "Clear name for this group "
                                                                "(e.g., 'Blue row', 'Basket 1', "
                                                                "'Left plate')"
                                                            )
                                                        },
                                                        "count": {
                                                            "type": "number",
                                                            "description": (
                                                                "Count for this specific group "
                                                                "(whole numbers or 0.5 "
                                                                "increments only)"
                                                            )
                                                        }
                                                    },
                                                    "required": ["group_identifier", "count"]
                                                }
                                            }
                                        },
                                        "required": ["object_name", "scenario_classification",
                                                    "counting_strategy_used", "method_1_count",
                                                    "method_1_details", "method_2_count",
                                                    "method_2_details", "method_3_count",
                                                    "method_3_details", "final_verified_count",
                                                    "confidence_level"]
                                    }
                                }
                            },
                            "required": ["image_url", "image_index", "overall_confidence",
                                        "image_rejected", "counting_process_summary",
                                        "object_types"]
                        }
                    }
                },
                "required": ["image_counts"]
            }
        }]

        logger.info(f"Counting objects in {len(image_urls)} image(s) without bias...")
        
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16384,
            system=system_prompt,
            tools=tools,
            tool_choice={"type": "tool", "name": "object_count_report"},
            messages=[{"role": "user", "content": message_content}]
        )
        
        # Extract counting results
        for content in response.content:
            if content.type == "tool_use" and content.name == "object_count_report":
                tool_input = content.input
                
                # Parse into our structured format
                image_counts = []
                for img_data in tool_input.get("image_counts", []):
                    object_types = []
                    for obj_data in img_data.get("object_types", []):
                        object_types.append(ObjectTypeCount(**obj_data))
                    
                    # Get the actual image URL based on the index
                    # Claude doesn't know the URL, so we need to map it ourselves
                    image_index = img_data["image_index"]
                    if image_index <= len(image_urls):
                        actual_image_url = image_urls[image_index - 1]
                    else:
                        actual_image_url = img_data.get("image_url", "UNKNOWN")
                    
                    image_counts.append(ImageCountData(
                        image_url=actual_image_url,
                        image_index=image_index,
                        overall_confidence=img_data["overall_confidence"],
                        image_rejected=img_data["image_rejected"],
                        rejection_reason=img_data.get("rejection_reason"),
                        counting_process_summary=img_data["counting_process_summary"],
                        object_types=object_types
                    ))
                
                logger.info(f"Successfully counted objects in {len(image_counts)} image(s)")
                return ObjectCountResult(
                    success=True,
                    image_counts=image_counts,
                    error_message=None
                )
        
        # Fallback if no tool use found
        logger.error("No object count data found in response")
        return ObjectCountResult(
            success=False,
            image_counts=[],
            error_message="No object count data found in response"
        )
        
    except Exception as e:
        logger.error(f"Error counting objects in images: {e}")
        return ObjectCountResult(
            success=False,
            image_counts=[],
            error_message=str(e)
        )


def format_count_data_for_prompt(count_result: ObjectCountResult) -> str:
    """
    Format object count data into a readable string for inclusion in evaluation prompts.
    
    Parameters
    ----------
    count_result : ObjectCountResult
        The counting results to format
        
    Returns
    -------
    str
        Formatted string describing the object counts
    """
    if not count_result.success:
        return "\n\nObject Counting Failed: " + str(count_result.error_message)
    
    if not count_result.image_counts:
        return ""
    
    output_parts = ["\n\n## UNBIASED OBJECT COUNT DATA"]
    output_parts.append(
        "\nThe following object counts were obtained through systematic, multi-method"
    )
    output_parts.append("verification WITHOUT knowledge of expected content. These counts are")
    output_parts.append("AUTHORITATIVE - do NOT attempt to re-count objects in the images.")
    
    for img_data in count_result.image_counts:
        output_parts.append(f"\n\n### Image: {img_data.image_url}")
        output_parts.append(f"Overall Confidence: {img_data.overall_confidence.upper()}")
        
        if img_data.image_rejected:
            output_parts.append(f"⚠️  IMAGE REJECTED: {img_data.rejection_reason}")
            continue
        
        output_parts.append(f"\nCounting Process: {img_data.counting_process_summary}")
        output_parts.append("\n**Object Counts:**")
        
        for obj_type in img_data.object_types:
            output_parts.append(f"\n- **{obj_type.object_name}**: {obj_type.final_verified_count}")
            output_parts.append(f"  - Confidence: {obj_type.confidence_level}")
            output_parts.append(f"  - Scenario: {obj_type.scenario_classification}")
            output_parts.append(f"  - Strategy: {obj_type.counting_strategy_used}")
            
            # Show group breakdown for grouped scenarios
            if obj_type.group_breakdown:
                output_parts.append("  - **Group Breakdown**:")
                for group in obj_type.group_breakdown:
                    output_parts.append(f"    * {group.group_identifier}: {group.count}")
                # Calculate and verify total
                group_total = sum(g.count for g in obj_type.group_breakdown)
                output_parts.append(f"    * Total: {group_total}")
            
            output_parts.append(f"  - Method Agreement: {obj_type.method_agreement}")
            
            if obj_type.container_relationship:
                output_parts.append(f"  - Relationship: {obj_type.container_relationship}")
            
            if obj_type.count_discrepancies:
                output_parts.append(f"  - Discrepancies Resolved: {obj_type.count_discrepancies}")
            
            # Show method details for transparency
            output_parts.append("  - Verification Details:")
            output_parts.append(
                f"    * Method 1: {obj_type.method_1_count} ({obj_type.method_1_details})"
            )
            output_parts.append(
                f"    * Method 2: {obj_type.method_2_count} ({obj_type.method_2_details})"
            )
            output_parts.append(
                f"    * Method 3: {obj_type.method_3_count} ({obj_type.method_3_details})"
            )
    
    return "\n".join(output_parts)

