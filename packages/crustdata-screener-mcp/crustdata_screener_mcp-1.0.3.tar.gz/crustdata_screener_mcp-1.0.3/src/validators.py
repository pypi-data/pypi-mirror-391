#!/usr/bin/env python3
"""
Validation utilities for CrustData MCP Server.

This module contains validation logic that mirrors the backend Django serializers
to ensure proper parameter validation before making API requests.
"""

import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse, parse_qs


class ValidationError(Exception):
    """Custom validation error exception."""
    pass


class BaseValidator:
    """Base class for validators with common utilities."""
    
    @staticmethod
    def is_linkedin_url(url: str, url_type: str = "company") -> bool:
        """
        Validate LinkedIn URL format.
        
        Args:
            url: URL to validate
            url_type: Type of LinkedIn URL - 'company', 'person', or 'school'
        
        Returns:
            bool: True if valid LinkedIn URL
        """
        if not url:
            return False
            
        # Normalize URL
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        if url_type == "company":
            pattern = r"^(?:https?://)?(?:www\.)?linkedin\.com/company/[\w-]+/?$"
        elif url_type == "person":
            pattern = r"^(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+/?$"
        elif url_type == "school":
            pattern = r"^(?:https?://)?(?:www\.)?linkedin\.com/school/[\w-]+/?$"
        else:
            return False
            
        return bool(re.match(pattern, url))
    
    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """
        Validate domain format.
        
        Args:
            domain: Domain to validate
        
        Returns:
            bool: True if valid domain
        """
        if not domain:
            return False
        
        # Basic domain pattern - allows subdomains, letters, numbers, hyphens
        pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        return bool(re.match(pattern, domain.strip()))
    
    @staticmethod
    def validate_integer_list(values: List[str], field_name: str) -> List[int]:
        """
        Validate and convert list of strings to integers.
        
        Args:
            values: List of string values
            field_name: Name of field for error messages
        
        Returns:
            List of integers
        
        Raises:
            ValidationError: If conversion fails
        """
        try:
            return [int(v.strip()) for v in values]
        except (ValueError, TypeError) as e:
            raise ValidationError(f"All {field_name} values must be integers") from e


class CompanyDataValidator(BaseValidator):
    """Validator for company data enrichment endpoint."""
    
    MAX_ITEMS = 25
    
    @classmethod
    def validate(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate company data query parameters.
        
        Args:
            params: Request parameters
        
        Returns:
            Validated parameters
        
        Raises:
            ValidationError: If validation fails
        """
        company_name = params.get("company_name")
        company_domain = params.get("company_domain")
        company_id = params.get("company_id")
        company_linkedin_url = params.get("company_linkedin_url")
        
        # Ensure at least one identifier is provided
        if not any([company_name, company_domain, company_id, company_linkedin_url]):
            raise ValidationError(
                "Either company_name, company_domain, company_linkedin_url, or company_id parameter is required"
            )
        
        # Ensure only one type of identifier
        identifiers_provided = sum(bool(x) for x in [company_name, company_domain, company_id, company_linkedin_url])
        if identifiers_provided > 1:
            raise ValidationError(
                "Please provide only one type of input: company_name, company_domain, company_linkedin_url, or company_id"
            )
        
        # Validate LinkedIn URLs
        if company_linkedin_url:
            urls = [url.strip() for url in company_linkedin_url.split(",")]
            if len(urls) > cls.MAX_ITEMS:
                raise ValidationError(f"You can only provide up to {cls.MAX_ITEMS} company LinkedIn URLs")
            
            invalid_urls = [url for url in urls if not cls.is_linkedin_url(url, "company")]
            if invalid_urls:
                raise ValidationError(f"Invalid LinkedIn company URLs: {', '.join(invalid_urls)}")
        
        # Validate domains
        if company_domain:
            domains = [d.strip() for d in company_domain.split(",")]
            if len(domains) > cls.MAX_ITEMS:
                raise ValidationError(f"You can only provide up to {cls.MAX_ITEMS} company domains")
            
            invalid_domains = [d for d in domains if not cls.is_valid_domain(d)]
            if invalid_domains:
                raise ValidationError(f"Invalid company domains: {', '.join(invalid_domains)}")
        
        # Validate company IDs
        if company_id:
            ids = [cid.strip() for cid in company_id.split(",")]
            if len(ids) > cls.MAX_ITEMS:
                raise ValidationError(f"You can only provide up to {cls.MAX_ITEMS} company IDs")
            
            try:
                cls.validate_integer_list(ids, "company_id")
            except ValidationError:
                raise
        
        # Validate company names
        if company_name:
            names = [n.strip() for n in company_name.split(",")]
            if len(names) > cls.MAX_ITEMS:
                raise ValidationError(f"You can only provide up to {cls.MAX_ITEMS} company names")
        
        return params


class IdentifyCompanyValidator(BaseValidator):
    """Validator for company identification endpoint."""
    
    @classmethod
    def validate(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate company identification parameters.
        
        Args:
            params: Request parameters
        
        Returns:
            Validated parameters
        
        Raises:
            ValidationError: If validation fails
        """
        query_company_name = params.get("query_company_name")
        query_company_website = params.get("query_company_website")
        query_company_linkedin_url = params.get("query_company_linkedin_url")
        query_company_crunchbase_url = params.get("query_company_crunchbase_url")
        query_company_id = params.get("query_company_id")
        count = params.get("count")
        
        all_identifiers = [
            query_company_name,
            query_company_website,
            query_company_linkedin_url,
            query_company_crunchbase_url,
            query_company_id,
        ]
        
        # At least one identifier required
        if not any(all_identifiers):
            raise ValidationError(
                "Either query_company_name, query_company_website, query_company_crunchbase_url, "
                "query_company_linkedin_url or query_company_id parameter is required"
            )
        
        # Only one identifier allowed
        if sum(bool(x) for x in all_identifiers) > 1:
            raise ValidationError(
                "Only one of query_company_name, query_company_website, query_company_crunchbase_url, "
                "query_company_linkedin_url or query_company_id parameter is allowed"
            )
        
        # Validate LinkedIn URL
        if query_company_linkedin_url:
            pattern = re.compile(r"^(?:https?://)?(?:www\.)?linkedin\.com/(company|school|in)/([^/?#]+)/?$")
            if not pattern.match(query_company_linkedin_url):
                raise ValidationError(
                    "Invalid LinkedIn URL. It should follow the pattern: "
                    "https://www.linkedin.com/in/company_name_or_id, "
                    "or https://www.linkedin.com/school/school_name_or_id, "
                    "or https://www.linkedin.com/company/company_name_or_id"
                )
        
        # Validate Crunchbase URL
        if query_company_crunchbase_url:
            pattern = re.compile(r"^(?:https?://)?(?:www\.)?crunchbase\.com/organization/([^/?#]+)/?$")
            if not pattern.match(query_company_crunchbase_url):
                raise ValidationError(
                    "Invalid Crunchbase URL. It should follow the pattern: "
                    "https://www.crunchbase.com/organization/organization_name_or_id"
                )
        
        # Validate website domain
        if query_company_website and not cls.is_valid_domain(query_company_website):
            raise ValidationError("Invalid website URL.")
        
        # Validate company ID
        if query_company_id:
            try:
                int(query_company_id)
            except (ValueError, TypeError) as e:
                raise ValidationError("company_id must be an integer") from e
        
        # Validate count
        if count is not None:
            try:
                count_int = int(count)
                if count_int < 1 or count_int > 25:
                    raise ValidationError("Count must be between 1 and 25.")
            except (ValueError, TypeError):
                raise ValidationError("Count must be an integer")
        
        return params


class PersonEnrichmentValidator(BaseValidator):
    """Validator for person enrichment endpoint."""
    
    MAX_PROFILES = 25
    
    EXCLUDED_EMAIL_DOMAINS = {
        "resource.calendar.google.com",
        "calendar.google.com",
        "calendar.outlook.com",
        "calendar.yahoo.com",
        "calendar.icloud.com",
        "calendar.zoho.com",
        "calendar.protonmail.com",
    }
    
    COMMON_EMAIL_PROVIDERS = {
        "gmail", "yahoo", "hotmail", "outlook", "aol", "icloud", "protonmail"
    }
    
    @classmethod
    def validate(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate person enrichment parameters.
        
        Args:
            params: Request parameters
        
        Returns:
            Validated parameters
        
        Raises:
            ValidationError: If validation fails
        """
        linkedin_url = params.get("linkedin_profile_url") or params.get("person_linkedin_url")
        business_email = params.get("business_email") or params.get("person_email")
        force_fetch = params.get("force_fetch", False)
        enrich_realtime = params.get("enrich_realtime", False)
        open_to_cards = params.get("open_to_cards", False)
        min_similarity_score = params.get("min_similarity_score")
        
        # Must provide either LinkedIn URL or business email
        if not linkedin_url and not business_email:
            raise ValidationError("You must provide either a LinkedIn profile URL or a business email.")
        
        if linkedin_url and business_email:
            raise ValidationError(
                "You can only enrich using either a LinkedIn profile URL or a business email, not both."
            )
        
        # Validate force_fetch and enrich_realtime dependency
        if force_fetch and not enrich_realtime:
            raise ValidationError("force_fetch can only be used with enrich_realtime.")
        
        if open_to_cards and not enrich_realtime:
            raise ValidationError("open_to_cards can only be used with enrich_realtime.")
        
        if min_similarity_score and not business_email:
            raise ValidationError("min_similarity_score can only be used with business_email.")
        
        # Validate LinkedIn URLs
        if linkedin_url:
            urls = [url.strip() for url in linkedin_url.split(",")]
            if len(urls) > cls.MAX_PROFILES:
                raise ValidationError(f"You can only enrich up to {cls.MAX_PROFILES} LinkedIn profiles at a time.")
            
            for url in urls:
                if not cls.is_linkedin_url(url, "person"):
                    raise ValidationError(f"Invalid LinkedIn URL format: {url}")
        
        # Validate business email
        if business_email:
            emails = business_email.split(",")
            if len(emails) > 1:
                raise ValidationError("You can only enrich one business email at a time.")
            
            # Basic email validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, business_email):
                raise ValidationError(f"Invalid email address format: {business_email}")
            
            domain = business_email.split("@")[1].lower()
            
            # Check common email providers
            if domain.split(".")[0] in cls.COMMON_EMAIL_PROVIDERS:
                raise ValidationError(
                    f"The email {business_email} appears to be a personal email. Please provide a valid business email."
                )
            
            # Check excluded domains
            if domain in cls.EXCLUDED_EMAIL_DOMAINS:
                raise ValidationError(
                    f"The email domain {domain} is not supported for calendar invites and automated systems."
                )
        
        return params


class LinkedInPostsValidator(BaseValidator):
    """Validator for LinkedIn posts endpoint."""
    
    POST_TYPES = ["IMAGE", "VIDEO", "ARTICLE", "TEXT"]
    
    @classmethod
    def validate(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate LinkedIn posts parameters.
        
        Args:
            params: Request parameters
        
        Returns:
            Validated parameters
        
        Raises:
            ValidationError: If validation fails
        """
        person_linkedin_url = params.get("person_linkedin_url")
        company_linkedin_url = params.get("company_linkedin_url")
        linkedin_post_url = params.get("linkedin_post_url")
        limit = params.get("limit")
        page = params.get("page")
        post_types = params.get("post_types")
        max_reactors = params.get("max_reactors", 0)
        max_comments = params.get("max_comments", 0)
        fields = params.get("fields", "")
        
        # Validate mutually exclusive parameters
        provided_urls = sum(bool(x) for x in [person_linkedin_url, company_linkedin_url, linkedin_post_url])
        if provided_urls > 1:
            raise ValidationError(
                "Only one of 'person_linkedin_url', 'company_linkedin_url', or 'linkedin_post_url' can be provided"
            )
        
        if not provided_urls:
            raise ValidationError(
                "One of 'person_linkedin_url', 'company_linkedin_url', or 'linkedin_post_url' is required"
            )
        
        # Validate LinkedIn post URL
        if linkedin_post_url:
            if not any(domain in linkedin_post_url for domain in ["linkedin.com/feed/update/", "linkedin.com/posts/"]):
                raise ValidationError(
                    "Invalid LinkedIn post URL format. Expected format: https://www.linkedin.com/feed/update/urn:li:activity:<id>"
                )
        
        # Validate pagination
        if page and limit:
            raise ValidationError("Only one of 'page' or 'limit' can be provided, not both")
        
        if not page and not limit:
            raise ValidationError("Either 'page' or 'limit' must be provided")
        
        # Validate limit
        if limit:
            try:
                limit_int = int(limit)
                if limit_int < 1 or limit_int > 100:
                    raise ValidationError("'limit' must be between 1 and 100")
            except (ValueError, TypeError):
                raise ValidationError("'limit' must be an integer")
        
        # Validate page
        if page:
            try:
                page_int = int(page)
                if page_int < 1 or page_int > 20:
                    raise ValidationError("'page' must be between 1 and 20")
            except (ValueError, TypeError):
                raise ValidationError("'page' must be an integer")
        
        # Validate post types
        if post_types:
            types_list = [t.strip() for t in post_types.split(",")]
            invalid_types = [t for t in types_list if t not in cls.POST_TYPES]
            if invalid_types:
                raise ValidationError(
                    f"Invalid post type(s): {', '.join(invalid_types)}. Valid types are: {', '.join(cls.POST_TYPES)}"
                )
        
        # Validate max_reactors and max_comments
        if max_reactors:
            try:
                reactors_int = int(max_reactors)
                if reactors_int < 0 or reactors_int > 5000:
                    raise ValidationError("'max_reactors' must be between 0 and 5000")
            except (ValueError, TypeError):
                raise ValidationError("'max_reactors' must be an integer")
        
        if max_comments:
            try:
                comments_int = int(max_comments)
                if comments_int < 0 or comments_int > 5000:
                    raise ValidationError("'max_comments' must be between 0 and 5000")
            except (ValueError, TypeError):
                raise ValidationError("'max_comments' must be an integer")
        
        # Validate fields dependency
        fields_list = [f.strip() for f in fields.split(",")] if fields else []
        if max_reactors and "reactors" not in fields_list:
            raise ValidationError("'reactors' is required in fields when 'max_reactors' is provided")
        
        if max_comments and "comments" not in fields_list:
            raise ValidationError("'comments' is required in fields when 'max_comments' is provided")
        
        return params


class PersonSearchValidator(BaseValidator):
    """Validator for person search endpoint."""
    
    @classmethod
    def validate(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate person search parameters.
        
        Args:
            params: Request parameters
        
        Returns:
            Validated parameters
        
        Raises:
            ValidationError: If validation fails
        """
        job_id = params.get("job_id")
        linkedin_sales_navigator_search_url = params.get("linkedin_sales_navigator_search_url")
        filters = params.get("filters")
        page = params.get("page")
        limit = params.get("limit")
        background_job = params.get("background_job")
        post_processing = params.get("post_processing", {})
        preview = params.get("preview", False)
        
        # Job ID validation
        if job_id:
            if any([linkedin_sales_navigator_search_url, filters, page, limit, background_job, post_processing]):
                raise ValidationError("When 'job_id' is provided, no other fields should be included.")
            return params
        
        # Basic validation
        if not linkedin_sales_navigator_search_url and not filters:
            raise ValidationError("Either 'filters' or 'linkedin_sales_navigator_search_url' is required")
        
        if linkedin_sales_navigator_search_url and filters:
            raise ValidationError(
                "Both 'filters' and 'linkedin_sales_navigator_search_url' are not allowed together"
            )
        
        # Validate LinkedIn Sales Navigator URL
        if linkedin_sales_navigator_search_url:
            parsed_url = urlparse(linkedin_sales_navigator_search_url)
            
            if parsed_url.netloc != "www.linkedin.com":
                raise ValidationError("Invalid LinkedIn domain")
            
            if "/sales/search/people" not in parsed_url.path:
                raise ValidationError("Invalid LinkedIn Sales Navigator search path. Expected /sales/search/people")
            
            query_string = parsed_url.query or parsed_url.fragment
            query_params = parse_qs(query_string)
            
            if "query" not in query_params:
                raise ValidationError("Missing 'query' parameter in URL")
        
        # Validate filters
        if filters:
            if not isinstance(filters, list):
                raise ValidationError("'filters' must be an array/list")
            
            if page is not None and limit is not None and limit > 25:
                raise ValidationError("When 'page' is provided, 'limit' cannot exceed 25")
            
            if page is None and limit is None and not preview:
                raise ValidationError("Either 'page', 'limit' or 'preview' must be provided when using filters")
        
        # Validate preview
        if preview and (job_id or limit or background_job or post_processing or page):
            raise ValidationError("preview cannot be used with job_id, limit, background_job, post_processing or page")
        
        # Validate limit
        if limit:
            try:
                limit_int = int(limit)
                if limit_int < 1 or limit_int > 10000:
                    raise ValidationError("'limit' must be between 1 and 10000")
            except (ValueError, TypeError):
                raise ValidationError("'limit' must be an integer")
        
        # Validate page
        if page:
            try:
                page_int = int(page)
                if page_int < 1:
                    raise ValidationError("'page' must be a positive integer")
            except (ValueError, TypeError):
                raise ValidationError("'page' must be an integer")
        
        # Validate post_processing
        if post_processing:
            exclude_profiles = post_processing.get("exclude_profiles", [])
            if exclude_profiles and not isinstance(exclude_profiles, list):
                raise ValidationError("'exclude_profiles' must be a list")
            
            for url in exclude_profiles:
                if not cls.is_linkedin_url(url, "person"):
                    raise ValidationError(f"Invalid LinkedIn profile URL in exclude_profiles: {url}")
        
        return params


class CompanyEmployeesValidator(BaseValidator):
    """Validator for company employees export endpoint."""
    
    @classmethod
    def validate(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate company employees parameters.
        
        Args:
            params: Request parameters
        
        Returns:
            Validated parameters
        
        Raises:
            ValidationError: If validation fails
        """
        company_linkedin_id = params.get("company_linkedin_id")
        company_id = params.get("company_id")
        company_name = params.get("company_name")
        s3_username = params.get("s3_username")
        job_id = params.get("job_id")
        version = params.get("version", "v2")
        
        # Validate version
        if version not in ["v1", "v2"]:
            raise ValidationError("Version must be 'v1' or 'v2'.")
        
        # Job ID validation
        if job_id:
            # When checking job status, other fields are not required
            return params
        
        # For non-job_id requests, require s3_username
        if not s3_username:
            raise ValidationError("s3_username is required when job_id is not provided.")
        
        # Validate s3_username pattern
        s3_username_pattern = re.compile(r"^ext-[a-zA-Z0-9]+-crustdata$")
        if not s3_username_pattern.match(s3_username):
            raise ValidationError("Please provide a valid s3_username.")
        
        # Check company identifiers
        company_identifiers = [
            bool(company_linkedin_id is not None),
            bool(company_id is not None),
            bool(company_name and company_name.strip())
        ]
        
        # Ensure exactly one identifier
        if not any(company_identifiers):
            raise ValidationError("One of company_linkedin_id, company_id, or company_name is required.")
        
        if sum(company_identifiers) > 1:
            raise ValidationError("Only one of company_linkedin_id, company_id, or company_name is allowed.")
        
        return params


# Validator registry mapping tool names to validator classes
VALIDATOR_REGISTRY = {
    "enrich_company_data": CompanyDataValidator,
    "identify_company": IdentifyCompanyValidator,
    "enrich_person_profile": PersonEnrichmentValidator,
    "get_linkedin_posts": LinkedInPostsValidator,
    "search_people": PersonSearchValidator,
    "get_company_employees": CompanyEmployeesValidator,
}


def validate_tool_params(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate tool parameters before making API requests.
    
    Args:
        tool_name: Name of the tool being called
        params: Parameters to validate
    
    Returns:
        Validated parameters
    
    Raises:
        ValidationError: If validation fails
    """
    validator_class = VALIDATOR_REGISTRY.get(tool_name)
    
    if not validator_class:
        # No validator defined for this tool, pass through
        return params
    
    return validator_class.validate(params)
