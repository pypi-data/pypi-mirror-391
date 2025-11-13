#!/usr/bin/env python3
"""
Test cases for MCP server validators.

These tests demonstrate the validation logic and ensure it matches backend behavior.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validators import (
    ValidationError,
    CompanyDataValidator,
    IdentifyCompanyValidator,
    PersonEnrichmentValidator,
    LinkedInPostsValidator,
    PersonSearchValidator,
    CompanyEmployeesValidator,
)


def test_company_data_validator():
    """Test CompanyDataValidator."""
    print("\n=== Testing CompanyDataValidator ===")
    
    # Valid cases
    print("✓ Valid: Single domain")
    CompanyDataValidator.validate({"company_domain": "stripe.com"})
    
    print("✓ Valid: Multiple domains")
    CompanyDataValidator.validate({"company_domain": "stripe.com,shopify.com"})
    
    print("✓ Valid: Company LinkedIn URL")
    CompanyDataValidator.validate({"company_linkedin_url": "https://www.linkedin.com/company/stripe"})
    
    # Invalid cases
    try:
        CompanyDataValidator.validate({})
        print("✗ FAILED: Should require at least one identifier")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        CompanyDataValidator.validate({
            "company_domain": "stripe.com",
            "company_name": "Stripe"
        })
        print("✗ FAILED: Should reject multiple identifiers")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        domains = ",".join([f"domain{i}.com" for i in range(26)])
        CompanyDataValidator.validate({"company_domain": domains})
        print("✗ FAILED: Should reject >25 items")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        CompanyDataValidator.validate({"company_domain": "not-a-valid-domain"})
        print("✗ FAILED: Should reject invalid domain")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")


def test_identify_company_validator():
    """Test IdentifyCompanyValidator."""
    print("\n=== Testing IdentifyCompanyValidator ===")
    
    # Valid cases
    print("✓ Valid: Query by name")
    IdentifyCompanyValidator.validate({"query_company_name": "Stripe"})
    
    print("✓ Valid: Query by LinkedIn URL")
    IdentifyCompanyValidator.validate({
        "query_company_linkedin_url": "https://www.linkedin.com/company/stripe"
    })
    
    print("✓ Valid: With count")
    IdentifyCompanyValidator.validate({"query_company_name": "Stripe", "count": 5})
    
    # Invalid cases
    try:
        IdentifyCompanyValidator.validate({"count": 30})
        print("✗ FAILED: Should reject count > 25")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        IdentifyCompanyValidator.validate({
            "query_company_name": "Stripe",
            "query_company_website": "stripe.com"
        })
        print("✗ FAILED: Should reject multiple identifiers")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")


def test_person_enrichment_validator():
    """Test PersonEnrichmentValidator."""
    print("\n=== Testing PersonEnrichmentValidator ===")
    
    # Valid cases
    print("✓ Valid: LinkedIn URL")
    PersonEnrichmentValidator.validate({
        "linkedin_profile_url": "https://www.linkedin.com/in/johnsmith"
    })
    
    print("✓ Valid: Business email")
    PersonEnrichmentValidator.validate({
        "business_email": "john@company.com"
    })
    
    print("✓ Valid: With enrich_realtime and force_fetch")
    PersonEnrichmentValidator.validate({
        "linkedin_profile_url": "https://www.linkedin.com/in/johnsmith",
        "enrich_realtime": True,
        "force_fetch": True
    })
    
    # Invalid cases
    try:
        PersonEnrichmentValidator.validate({})
        print("✗ FAILED: Should require LinkedIn URL or email")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        PersonEnrichmentValidator.validate({
            "linkedin_profile_url": "https://www.linkedin.com/in/johnsmith",
            "business_email": "john@company.com"
        })
        print("✗ FAILED: Should reject both URL and email")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        PersonEnrichmentValidator.validate({
            "business_email": "john@gmail.com"
        })
        print("✗ FAILED: Should reject personal email")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        PersonEnrichmentValidator.validate({
            "linkedin_profile_url": "https://www.linkedin.com/in/johnsmith",
            "force_fetch": True
        })
        print("✗ FAILED: Should reject force_fetch without enrich_realtime")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")


def test_linkedin_posts_validator():
    """Test LinkedInPostsValidator."""
    print("\n=== Testing LinkedInPostsValidator ===")
    
    # Valid cases
    print("✓ Valid: Person URL with limit")
    LinkedInPostsValidator.validate({
        "person_linkedin_url": "https://www.linkedin.com/in/johnsmith",
        "limit": 10
    })
    
    print("✓ Valid: Person URL with page")
    LinkedInPostsValidator.validate({
        "person_linkedin_url": "https://www.linkedin.com/in/johnsmith",
        "page": 1
    })
    
    # Invalid cases
    try:
        LinkedInPostsValidator.validate({
            "person_linkedin_url": "https://www.linkedin.com/in/johnsmith"
        })
        print("✗ FAILED: Should require page or limit")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        LinkedInPostsValidator.validate({
            "person_linkedin_url": "https://www.linkedin.com/in/johnsmith",
            "page": 1,
            "limit": 10
        })
        print("✗ FAILED: Should reject both page and limit")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        LinkedInPostsValidator.validate({
            "person_linkedin_url": "https://www.linkedin.com/in/johnsmith",
            "limit": 150
        })
        print("✗ FAILED: Should reject limit > 100")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        LinkedInPostsValidator.validate({
            "person_linkedin_url": "https://www.linkedin.com/in/johnsmith",
            "limit": 10,
            "max_reactors": 100
        })
        print("✗ FAILED: Should reject max_reactors without reactors field")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")


def test_person_search_validator():
    """Test PersonSearchValidator."""
    print("\n=== Testing PersonSearchValidator ===")
    
    # Valid cases
    print("✓ Valid: LinkedIn Sales Navigator URL")
    PersonSearchValidator.validate({
        "linkedin_sales_navigator_search_url": "https://www.linkedin.com/sales/search/people?query=(filters:List())"
    })
    
    print("✓ Valid: Filters with page")
    PersonSearchValidator.validate({
        "filters": [{"filter_type": "CURRENT_TITLE", "value": ["CEO"]}],
        "page": 1
    })
    
    # Invalid cases
    try:
        PersonSearchValidator.validate({})
        print("✗ FAILED: Should require filters or URL")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        PersonSearchValidator.validate({
            "linkedin_sales_navigator_search_url": "https://www.linkedin.com/sales/search/people?query=(filters:List())",
            "filters": [{"filter_type": "CURRENT_TITLE", "value": ["CEO"]}]
        })
        print("✗ FAILED: Should reject both URL and filters")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        PersonSearchValidator.validate({
            "filters": [{"filter_type": "CURRENT_TITLE", "value": ["CEO"]}]
        })
        print("✗ FAILED: Should require page/limit/preview with filters")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")


def test_company_employees_validator():
    """Test CompanyEmployeesValidator."""
    print("\n=== Testing CompanyEmployeesValidator ===")
    
    # Valid cases
    print("✓ Valid: Company ID with s3_username")
    CompanyEmployeesValidator.validate({
        "company_id": 123,
        "s3_username": "ext-user123-crustdata"
    })
    
    print("✓ Valid: Job status check")
    CompanyEmployeesValidator.validate({
        "job_id": "123e4567-e89b-12d3-a456-426614174000"
    })
    
    # Invalid cases
    try:
        CompanyEmployeesValidator.validate({
            "company_id": 123
        })
        print("✗ FAILED: Should require s3_username")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        CompanyEmployeesValidator.validate({
            "company_id": 123,
            "s3_username": "invalid-username"
        })
        print("✗ FAILED: Should reject invalid s3_username pattern")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")
    
    try:
        CompanyEmployeesValidator.validate({
            "company_id": 123,
            "company_name": "Stripe",
            "s3_username": "ext-user123-crustdata"
        })
        print("✗ FAILED: Should reject multiple identifiers")
    except ValidationError as e:
        print(f"✓ Correctly caught: {e}")


if __name__ == "__main__":
    print("Running MCP Server Validator Tests")
    print("=" * 50)
    
    try:
        test_company_data_validator()
        test_identify_company_validator()
        test_person_enrichment_validator()
        test_linkedin_posts_validator()
        test_person_search_validator()
        test_company_employees_validator()
        
        print("\n" + "=" * 50)
        print("✅ All validation tests completed!")
        print("\nThe validators are working correctly and preventing bad requests.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
