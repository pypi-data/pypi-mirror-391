"""Example: Using templates for document processing.

This example demonstrates how to use pre-configured templates
by their slug instead of defining schema and instructions inline.
"""

import asyncio
import os

from leapocr import LeapOCR, ProcessOptions


async def main():
    """Process documents using a template."""
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        raise ValueError("LEAPOCR_API_KEY environment variable not set")

    async with LeapOCR(api_key) as client:
        # Example 1: Use a template by slug
        print("Processing with invoice template...")
        job = await client.ocr.process_url(
            "https://example.com/invoice.pdf",
            options=ProcessOptions(
                template_slug="invoice-extraction",  # Reference existing template
            ),
        )
        result = await client.ocr.wait_until_done(job.job_id)

        print("✓ Processed using template")
        print(f"  Job ID: {result.job_id}")
        print(f"  Pages processed: {result.processed_pages}")
        print(f"  Credits used: {result.credits_used}")
        print(f"  Result format: {result.result_format}")
        print()

        # Example 2: Process multiple files with the same template
        print("Batch processing with template...")
        files = [
            "https://example.com/invoice1.pdf",
            "https://example.com/invoice2.pdf",
            "https://example.com/invoice3.pdf",
        ]

        # Submit all jobs
        jobs = await asyncio.gather(
            *[
                client.ocr.process_url(
                    url, options=ProcessOptions(template_slug="invoice-extraction")
                )
                for url in files
            ]
        )

        # Wait for all to complete
        results = await asyncio.gather(*[client.ocr.wait_until_done(job.job_id) for job in jobs])

        print(f"✓ Processed {len(results)} documents")
        total_credits = sum(r.credits_used for r in results)
        print(f"  Total credits: {total_credits}")
        print()

        # Example 3: Use different templates for different document types
        print("Processing different document types...")

        contracts_job = await client.ocr.process_file(
            "contract.pdf",
            options=ProcessOptions(template_slug="contract-analysis"),
        )
        await client.ocr.wait_until_done(contracts_job.job_id)

        receipts_job = await client.ocr.process_file(
            "receipt.pdf",
            options=ProcessOptions(template_slug="receipt-extraction"),
        )
        await client.ocr.wait_until_done(receipts_job.job_id)

        print("✓ Contract processed")
        print("✓ Receipt processed")


if __name__ == "__main__":
    asyncio.run(main())
