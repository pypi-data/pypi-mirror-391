"""Example: Model selection and custom models.

This example demonstrates how to use different OCR models,
including predefined models and custom organization-specific models.
"""

import asyncio
import os

from leapocr import Format, LeapOCR, Model, ProcessOptions


async def main():
    """Process documents with different models."""
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        raise ValueError("LEAPOCR_API_KEY environment variable not set")

    async with LeapOCR(api_key) as client:
        # Example 1: Standard model (default, 1 credit per page)
        print("Processing with standard model...")
        job1 = await client.ocr.process_url(
            "https://example.com/document.pdf",
            options=ProcessOptions(
                format=Format.STRUCTURED,
                model=Model.STANDARD_V1,
            ),
        )
        standard_result = await client.ocr.wait_until_done(job1.job_id)

        print("✓ Standard model processing complete")
        print(f"  Credits used: {standard_result.credits_used}")
        print(f"  Processing time: {standard_result.processing_time_seconds:.2f}s")
        print()

        # Example 2: English Pro model (high accuracy for English, 2 credits per page)
        print("Processing with English Pro model...")
        job2 = await client.ocr.process_url(
            "https://example.com/english-document.pdf",
            options=ProcessOptions(
                format=Format.STRUCTURED,
                model=Model.ENGLISH_PRO_V1,
                instructions="Extract all structured data with high precision",
            ),
        )
        english_pro_result = await client.ocr.wait_until_done(job2.job_id)

        print("✓ English Pro model processing complete")
        print(f"  Credits used: {english_pro_result.credits_used}")
        print(f"  Processing time: {english_pro_result.processing_time_seconds:.2f}s")
        print()

        # Example 3: Pro model (premium multilingual, 2 credits per page)
        print("Processing with Pro model...")
        job3 = await client.ocr.process_url(
            "https://example.com/multilingual-document.pdf",
            options=ProcessOptions(
                format=Format.STRUCTURED,
                model=Model.PRO_V1,
                instructions="Process multilingual content",
            ),
        )
        pro_result = await client.ocr.wait_until_done(job3.job_id)

        print("✓ Pro model processing complete")
        print(f"  Credits used: {pro_result.credits_used}")
        print(f"  Processing time: {pro_result.processing_time_seconds:.2f}s")
        print()

        # Example 4: Custom model (organization-specific)
        print("Processing with custom model...")
        job4 = await client.ocr.process_url(
            "https://example.com/specialized-document.pdf",
            options=ProcessOptions(
                format=Format.STRUCTURED,
                model="my-organization-model-v1",  # Custom string model
                instructions="Use custom extraction logic",
            ),
        )
        custom_result = await client.ocr.wait_until_done(job4.job_id)

        print("✓ Custom model processing complete")
        print(f"  Model used: {custom_result.model}")
        print(f"  Credits used: {custom_result.credits_used}")
        print()

        # Example 5: Model comparison
        print("Comparing model performance...")
        test_url = "https://example.com/test-document.pdf"

        # Submit all jobs concurrently
        jobs = await asyncio.gather(
            client.ocr.process_url(test_url, options=ProcessOptions(model=Model.STANDARD_V1)),
            client.ocr.process_url(test_url, options=ProcessOptions(model=Model.ENGLISH_PRO_V1)),
            client.ocr.process_url(test_url, options=ProcessOptions(model=Model.PRO_V1)),
        )

        # Wait for all to complete
        results = await asyncio.gather(*[client.ocr.wait_until_done(job.job_id) for job in jobs])

        print("Model comparison results:")
        for result in results:
            print(f"  {result.model}:")
            print(f"    Credits: {result.credits_used}")
            print(f"    Time: {result.processing_time_seconds:.2f}s")
            print(f"    Pages: {result.processed_pages}")


if __name__ == "__main__":
    asyncio.run(main())
