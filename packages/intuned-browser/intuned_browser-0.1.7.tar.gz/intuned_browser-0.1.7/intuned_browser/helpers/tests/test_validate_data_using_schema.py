import logging
from typing import Any

import pytest

from intuned_browser import validate_data_using_schema
from intuned_browser.helpers.types import ValidationError


@pytest.mark.asyncio
async def test_validate_data_using_schema_valid() -> None:
    """Test validation with valid data."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    }

    data: dict[str, Any] = {
        "name": "John Doe",
        "age": 30,
        "extra_field": "allowed",
    }

    validate_data_using_schema(data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_invalid() -> None:
    """Test validation with invalid data (missing required field)."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    }

    invalid_data: dict[str, Any] = {"name": "John Doe"}  # Missing required 'age' field

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    assert "Data validation failed" in str(exc_info.value)
    assert exc_info.value.data == invalid_data


@pytest.mark.asyncio
async def test_validate_data_using_schema_list() -> None:
    """Test validation with list of valid objects."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"],
        },
    }

    data: list[dict[str, Any]] = [
        {"name": "John Doe", "age": 30, "extra": "field"},
        {"name": "Jane Doe", "age": 25, "other": "value"},
    ]

    validate_data_using_schema(data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_list_invalid() -> None:
    """Test validation with list containing invalid object."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"],
        },
    }

    invalid_data: list[dict[str, Any]] = [
        {"name": "John Doe", "age": 30},
        {"name": "Jane Doe", "age": "25"},  # age should be integer, not string
    ]

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    logging.debug(f"exc_info: {exc_info}")
    assert "Data validation failed" in str(exc_info.value)
    assert exc_info.value.data == invalid_data


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_type() -> None:
    """Test validation with Attachment custom type."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
            "name": {"type": "string"},
        },
        "required": ["file", "name"],
    }

    # Valid data that matches Attachment structure
    valid_data: dict[str, Any] = {
        "file": {
            "file_name": "documents/report.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "documents/report.pdf",
            "endpoint": None,
            "suggested_file_name": "Monthly Report.pdf",
            "file_type": "document",
        },
        "name": "Test File Upload",
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_type_invalid() -> None:
    """Test validation with invalid Attachment data."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
            "name": {"type": "string"},
        },
        "required": ["file", "name"],
    }

    # Invalid data - missing required Attachment fields
    invalid_data: dict[str, Any] = {
        "file": {
            "file_name": "documents/report.pdf",
            # Missing required fields: bucket, region, suggested_file_name
        },
        "name": "Test File Upload",
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    assert "Data validation failed" in str(exc_info.value)
    assert exc_info.value.data == invalid_data


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_minimal_fields() -> None:
    """Test validation with Attachment containing only required fields."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
        },
        "required": ["file"],
    }

    # Valid data with only required fields
    valid_data: dict[str, Any] = {
        "file": {
            "file_name": "report.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "key": "files/report.pdf",
            "suggested_file_name": "Report.pdf",
        },
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_array() -> None:
    """Test validation with array of Attachments."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "attachments": {
                "type": "array",
                "items": {"type": "attachment"},
            },
        },
        "required": ["attachments"],
    }

    # Valid data with array of attachments
    valid_data: dict[str, Any] = {
        "attachments": [
            {
                "file_name": "doc1.pdf",
                "bucket": "my-bucket",
                "region": "us-east-1",
                "key": "files/doc1.pdf",
                "suggested_file_name": "Document 1.pdf",
                "endpoint": None,
                "file_type": "document",
            },
            {
                "file_name": "doc2.pdf",
                "bucket": "my-bucket",
                "region": "us-west-2",
                "key": "files/doc2.pdf",
                "suggested_file_name": "Document 2.pdf",
            },
        ],
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_array_invalid() -> None:
    """Test validation with array containing invalid Attachment."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "attachments": {
                "type": "array",
                "items": {"type": "attachment"},
            },
        },
        "required": ["attachments"],
    }

    # Invalid data - second attachment missing required fields
    invalid_data: dict[str, Any] = {
        "attachments": [
            {
                "file_name": "doc1.pdf",
                "bucket": "my-bucket",
                "region": "us-east-1",
                "key": "files/doc1.pdf",
                "suggested_file_name": "Document 1.pdf",
            },
            {
                "file_name": "doc2.pdf",
                # Missing bucket, region, key, suggested_file_name
            },
        ],
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    assert "Data validation failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_empty_array() -> None:
    """Test validation with empty array of Attachments."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "attachments": {
                "type": "array",
                "items": {"type": "attachment"},
            },
        },
        "required": ["attachments"],
    }

    # Valid data with empty array
    valid_data: dict[str, Any] = {
        "attachments": [],
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_optional_attachment() -> None:
    """Test validation with optional Attachment field."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
            "name": {"type": "string"},
        },
        "required": ["name"],  # file is optional
    }

    # Valid data without the optional attachment field
    valid_data: dict[str, Any] = {
        "name": "Test Without File",
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_multiple_attachments() -> None:
    """Test validation with multiple Attachment fields."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "primary_file": {"type": "attachment"},
            "backup_file": {"type": "attachment"},
            "title": {"type": "string"},
        },
        "required": ["primary_file", "title"],
    }

    # Valid data with multiple attachments
    valid_data: dict[str, Any] = {
        "primary_file": {
            "file_name": "main.pdf",
            "bucket": "primary-bucket",
            "region": "us-east-1",
            "key": "files/main.pdf",
            "suggested_file_name": "Main Document.pdf",
        },
        "backup_file": {
            "file_name": "backup.pdf",
            "bucket": "backup-bucket",
            "region": "us-west-2",
            "key": "files/backup.pdf",
            "suggested_file_name": "Backup Document.pdf",
        },
        "title": "Important Documents",
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_wrong_field_type() -> None:
    """Test validation with Attachment having wrong field type."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
        },
        "required": ["file"],
    }

    # Invalid data - bucket should be string, not integer
    invalid_data: dict[str, Any] = {
        "file": {
            "file_name": "report.pdf",
            "bucket": 12345,  # Should be string
            "region": "us-east-1",
            "key": "files/report.pdf",
            "suggested_file_name": "Report.pdf",
        },
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    assert "Data validation failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_with_endpoint() -> None:
    """Test validation with Attachment having custom endpoint."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
        },
        "required": ["file"],
    }

    # Valid data with custom endpoint (e.g., for R2/custom S3)
    valid_data: dict[str, Any] = {
        "file": {
            "file_name": "report.pdf",
            "bucket": "my-bucket",
            "region": "auto",
            "key": "files/report.pdf",
            "suggested_file_name": "Report.pdf",
            "endpoint": "https://custom-s3.example.com",
            "file_type": "document",
        },
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_fadi() -> None:
    """Test validation with invalid Attachment data."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Notice",
        "type": "object",
        "required": [
            "source_url",
            "solicitation_id",
            "state",
            "title",
            "issue_date",
            "due_date",
            "organization",
            "description",
            "preBidConference",
            "contacts",
            "attachments",
            "source_text",
        ],
        "properties": {
            "source_url": {"type": "string", "description": "MANDATORY - Source URL of the notice"},
            "solicitation_id": {"type": "string", "description": "MANDATORY - Unique solicitation identifier"},
            "state": {"type": "string", "description": "MANDATORY - State code (e.g., NY, GA)"},
            "title": {
                "type": "string",
                "description": "MANDATORY - Title of the notice, defaults to STATE - SOLICITATION ID",
            },
            "issue_date": {
                "type": ["string", "null"],
                "description": "Date the notice was posted, null if not available",
            },
            "due_date": {"type": ["string", "null"], "description": "Date the notice is due, null if not available"},
            "organization": {
                "type": ["string", "null"],
                "description": "Agency, department, or sub-state-level organization, null if not available",
            },
            "description": {
                "type": "array",
                "description": "Array of description objects, can be empty",
                "items": {"$ref": "#/definitions/Description"},
            },
            "preBidConference": {
                "oneOf": [{"$ref": "#/definitions/PreBidConference"}, {"type": "null"}],
                "description": "Pre-bid conference details, null if not available",
            },
            "contacts": {
                "type": "array",
                "description": "Array of contact objects, can be empty",
                "items": {"$ref": "#/definitions/Contact"},
            },
            "attachments": {
                "type": "array",
                "description": "Array of attachment objects, can be empty",
                "items": {"$ref": "#/definitions/Attachment"},
            },
            "source_text": {
                "type": "string",
                "description": "MANDATORY - Full text extracted from the source page HTML",
            },
        },
        "additionalProperties": False,
        "definitions": {
            "Description": {
                "type": "object",
                "required": ["title", "content"],
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the description block, defaults to 'Description'",
                    },
                    "content": {"type": "string", "description": "Content of the description"},
                },
                "additionalProperties": False,
            },
            "PreBidConference": {
                "type": "object",
                "required": ["mandatory", "date", "time", "location", "notes"],
                "properties": {
                    "mandatory": {
                        "type": ["boolean", "null"],
                        "description": "Whether the prebid conference is mandatory, null if not available",
                    },
                    "date": {
                        "type": ["string", "null"],
                        "description": "Date of the prebid conference, null if not available",
                    },
                    "time": {
                        "type": ["string", "null"],
                        "description": "Time of the prebid conference, null if not available",
                    },
                    "location": {
                        "type": ["string", "null"],
                        "description": "Location of the prebid conference, null if not available",
                    },
                    "notes": {
                        "type": ["string", "null"],
                        "description": "Additional text related to the prebid conference, null if not available",
                    },
                },
                "additionalProperties": False,
            },
            "Contact": {
                "type": "object",
                "required": ["name", "email", "phone", "fax"],
                "properties": {
                    "name": {"type": ["string", "null"], "description": "Contact name, null if not available"},
                    "email": {"type": ["string", "null"], "description": "Contact email, null if not available"},
                    "phone": {"type": ["string", "null"], "description": "Contact phone number, null if not available"},
                    "fax": {"type": ["string", "null"], "description": "Contact fax number, null if not available"},
                },
                "additionalProperties": False,
            },
            "Attachment": {
                "type": "object",
                "required": ["filename", "key", "suggested_filename"],
                "properties": {
                    "filename": {"type": "string", "description": "Original filename"},
                    "key": {"type": "string", "description": "Storage key or path"},
                    "suggested_filename": {"type": "string", "description": "Suggested filename for download"},
                },
                "additionalProperties": False,
            },
        },
    }
    data = {
        "source_url": "https://www.vermontbusinessregistry.com/BidPreview.aspx?BidID=69941",
        "solicitation_id": "69941",
        "state": "VT",
        "title": "#ref",
        "issue_date": "10/2/2025",
        "due_date": None,  # Testing nullable required field
        "organization": None,  # Testing nullable required field
        "description": [
            {
                "title": "Bid Description",
                "content": "HVAC system renovation project for Town of Chittenden.",
            }
        ],
        "preBidConference": {
            "mandatory": False,
            "date": None,
            "time": None,
            "location": None,
            "notes": None,
        },
        "contacts": [
            {
                "name": "Daniel Dupras",
                "email": None,  # Testing nullable field in nested object
                "phone": "(802) 855-1010",
                "fax": None,
            }
        ],
        "attachments": [],
        "source_text": "Sample source text from the page.",
    }
    validate_data_using_schema(data, schema)
