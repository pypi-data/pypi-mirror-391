"""Example: Advanced job management including deletion.

This example demonstrates how to manage OCR jobs including
checking status, retrieving results, and deleting jobs.
"""

import asyncio
import os

from leapocr import JobStatusType, LeapOCR, ProcessOptions


async def main():
    """Demonstrate job management operations."""
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        raise ValueError("LEAPOCR_API_KEY environment variable not set")

    async with LeapOCR(api_key) as client:
        # Example 1: Submit job and track manually
        print("Submitting job for processing...")
        job = await client.ocr.process_file(
            "document.pdf",
            options=ProcessOptions(),
        )

        print(f"✓ Job submitted: {job.job_id}")
        print(f"  Status: {job.status.value}")
        print()

        # Example 2: Poll status manually
        print("Polling job status...")
        while True:
            status = await client.ocr.get_job_status(job.job_id)

            print(
                f"  Status: {status.status.value} | "
                f"Progress: {status.progress:.1f}% | "
                f"Pages: {status.processed_pages}/{status.total_pages}"
            )

            if status.status in [
                JobStatusType.COMPLETED,
                JobStatusType.FAILED,
                JobStatusType.PARTIALLY_DONE,
            ]:
                break

            await asyncio.sleep(2)

        print()

        # Example 3: Get results if successful
        if status.status == JobStatusType.COMPLETED:
            print("Retrieving results...")
            result = await client.ocr.get_results(job.job_id)

            print("✓ Results retrieved")
            print(f"  File: {result.file_name}")
            print(f"  Pages: {len(result.pages)}")
            print(f"  Credits used: {result.credits_used}")
            print(f"  Processing time: {result.processing_time_seconds:.2f}s")
            print()

        # Example 4: Delete job when no longer needed
        print("Deleting job...")
        delete_response = await client.ocr.delete_job(job.job_id)

        print("✓ Job deleted")
        print(f"  Response: {delete_response}")
        print()

        # Example 5: Batch job cleanup
        print("Batch job cleanup example...")

        # Submit multiple jobs
        job_ids = []
        for i in range(3):
            job = await client.ocr.process_file(f"document{i}.pdf")
            job_ids.append(job.job_id)
            print(f"  Submitted job {i + 1}: {job.job_id}")

        print()
        print("Cleaning up all jobs...")

        # Delete all jobs
        for job_id in job_ids:
            await client.ocr.delete_job(job_id)
            print(f"  ✓ Deleted: {job_id}")

        print()
        print("All jobs cleaned up!")


if __name__ == "__main__":
    asyncio.run(main())
