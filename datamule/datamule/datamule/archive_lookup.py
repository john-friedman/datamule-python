import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from ..helper import _process_cik_and_metadata_filters
from ..providers.providers import MAIN_API_ENDPOINT
from ..utils.format_accession import format_accession


API_BASE_URL = f"{MAIN_API_ENDPOINT.rstrip('/')}/v3/sec-filings-lookup"
DEFAULT_PAGE_SIZE = 25000

_PARAM_MAP = {
    "accession": "accessionNumber",
    "accession_number": "accessionNumber",
    "submission_type": "submissionType",
    "filing_date": "filingDate",
    "report_date": "reportDate",
    "detected_time": "detectedTime",
    "contains_xbrl": "containsXBRL",
    "document_type": "documentType",
}
_RANGE_PARAMS = {"filingDate", "reportDate", "detectedTime"}
_COLUMN_MAP = {
    "filingDate": "filing_date",
}
_METADATA_FILTER_KEYS = {
    "name",
    "start_date",
    "business_city",
    "business_stateOrCountry",
    "business_stateOrCountryDescription",
    "business_street1",
    "business_street2",
    "business_zipCode",
    "category",
    "description",
    "ein",
    "entityType",
    "exchanges",
    "fiscalYearEnd",
    "flags",
    "insiderTransactionForIssuerExists",
    "insiderTransactionForOwnerExists",
    "mailing_city",
    "mailing_stateOrCountry",
    "mailing_stateOrCountryDescription",
    "mailing_street1",
    "mailing_street2",
    "mailing_zipCode",
    "ownerOrg",
    "phone",
    "sic",
    "sicDescription",
    "stateOfIncorporation",
    "stateOfIncorporationDescription",
    "ticker",
    "tickers",
}
_LOOKUP_FILTER_KEYS = {
    "cik",
    "accession",
    "accession_number",
    "accessionNumber",
    "submission_type",
    "submissionType",
    "filing_date",
    "filingDate",
    "report_date",
    "reportDate",
    "detected_time",
    "detectedTime",
    "contains_xbrl",
    "containsXBRL",
    "document_type",
    "documentType",
    "filename",
    "sequence",
}


def _get_api_key(api_key):
    key = api_key or os.getenv("DATAMULE_API_KEY")
    if not key:
        raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key")
    return key


def _stringify(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _add_param(params, name, value):
    if value is None:
        return

    if name == "accessionNumber":
        if isinstance(value, (list, tuple, set)):
            if not value:
                return
            params[name] = ",".join(str(format_accession(item, "int")) for item in value)
        else:
            params[name] = str(format_accession(value, "int"))
        return

    if name in _RANGE_PARAMS and isinstance(value, tuple):
        if len(value) != 2:
            raise ValueError(f"{name} range must be a 2-item tuple.")
        params[f"{name}_START"] = _stringify(value[0])
        params[f"{name}_END"] = _stringify(value[1])
        return

    if isinstance(value, (list, tuple, set)):
        if not value:
            return
        params[name] = ",".join(_stringify(item) for item in value)
        return

    params[name] = _stringify(value)


def _build_params(filters):
    params = {}
    for key, value in filters.items():
        if value is None:
            continue
        _add_param(params, _PARAM_MAP.get(key, key), value)
    return params


def _build_filters(
    cik=None,
    ticker=None,
    accession=None,
    submission_type=None,
    filing_date=None,
    report_date=None,
    detected_time=None,
    contains_xbrl=None,
    document_type=None,
    filename=None,
    sequence=None,
    **metadata_filters,
):
    company_filters = {}
    lookup_filters = {}

    for key, value in metadata_filters.items():
        if key in _METADATA_FILTER_KEYS:
            company_filters[key] = value
        elif key in _LOOKUP_FILTER_KEYS:
            lookup_filters[key] = value

    if "ticker" in company_filters and ticker is None:
        ticker = company_filters.pop("ticker")

    cik = _process_cik_and_metadata_filters(cik, ticker, **company_filters)
    filters = {
        "cik": cik,
        "accession": accession,
        "submission_type": submission_type,
        "filing_date": filing_date,
        "report_date": report_date,
        "detected_time": detected_time,
        "contains_xbrl": contains_xbrl,
        "document_type": document_type,
        "filename": filename,
        "sequence": sequence,
    }
    filters.update({key: value for key, value in lookup_filters.items() if value is not None})
    return filters


def _request_page(endpoint, params, api_key):
    query = urllib.parse.urlencode(params)
    url = f"{API_BASE_URL}/{endpoint}"
    if query:
        url = f"{url}?{query}"

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "datamule-python",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8")
        try:
            error_payload = json.loads(error_body)
            message = error_payload.get("error", error_body)
        except json.JSONDecodeError:
            message = error_body
        raise Exception(f"API request failed ({exc.code}): {message}") from exc

    if not payload.get("success"):
        raise Exception(f"API request failed: {payload.get('error')}")

    return payload


def _validate_columnar_results(page_data):
    if not isinstance(page_data, dict):
        raise ValueError("Expected columnar lookup response data.")
    for column, values in page_data.items():
        if not isinstance(values, list):
            raise ValueError(f"Expected columnar lookup values for {column}.")


def _rows_returned(page_data):
    if not page_data:
        return 0
    return max(len(values) for values in page_data.values())


def _columnar_to_rows(page_data):
    _validate_columnar_results(page_data)
    rows = []
    row_count = _rows_returned(page_data)

    for row_index in range(row_count):
        row = {}
        for column, values in page_data.items():
            if row_index < len(values):
                row[_COLUMN_MAP.get(column, column)] = values[row_index]
        rows.append(row)

    return rows


def _filter_rows(rows, filtered_accession_numbers=None, skip_accession_numbers=None):
    if filtered_accession_numbers is not None:
        keep = {format_accession(item, "int") for item in filtered_accession_numbers}
        rows = [row for row in rows if format_accession(row["accession"], "int") in keep]

    if skip_accession_numbers is not None:
        skip = {format_accession(item, "int") for item in skip_accession_numbers}
        rows = [row for row in rows if format_accession(row["accession"], "int") not in skip]

    return rows


def _lookup_archive(
    endpoint,
    api_key=None,
    page=None,
    page_size=DEFAULT_PAGE_SIZE,
    quiet=False,
    include_metadata=False,
    filtered_accession_numbers=None,
    skip_accession_numbers=None,
    **filters,
):
    key = _get_api_key(api_key)
    params = _build_params(filters)
    params["pageSize"] = page_size

    current_page = page or 1
    single_page = page is not None
    rows = []
    summary = {
        "pages": 0,
        "rows": 0,
        "total_charge": 0,
        "remaining_balance": None,
    }
    start_time = time.time()

    while True:
        page_params = params.copy()
        page_params["page"] = current_page

        payload = _request_page(endpoint, page_params, key)
        page_data = payload.get("data", {})
        page_rows = _columnar_to_rows(page_data)
        rows.extend(page_rows)

        metadata = payload.get("metadata", {})
        billing = metadata.get("billing", {})
        pagination = metadata.get("pagination", {})
        page_charge = billing.get("total_charge", 0) or 0

        summary["pages"] += 1
        summary["rows"] += len(page_rows)
        summary["total_charge"] += page_charge
        summary["remaining_balance"] = billing.get("remaining_balance", summary["remaining_balance"])

        if single_page or not pagination.get("hasMore", False):
            break
        current_page += 1

    rows = _filter_rows(
        rows,
        filtered_accession_numbers=filtered_accession_numbers,
        skip_accession_numbers=skip_accession_numbers,
    )
    summary["rows"] = len(rows)
    summary["elapsed_seconds"] = time.time() - start_time

    if not quiet:
        remaining = summary["remaining_balance"]
        remaining_text = "unknown" if remaining is None else f"${remaining:.2f}"
        print("\nArchive lookup complete:")
        print(f"- Retrieved {summary['rows']} records across {summary['pages']} pages")
        print(f"- Total cost: ${summary['total_charge']:.4f}")
        print(f"- Remaining balance: {remaining_text}")

    if include_metadata:
        return rows, summary
    return rows


def lookup_archive_sgml(
    cik=None,
    ticker=None,
    accession=None,
    submission_type=None,
    filing_date=None,
    report_date=None,
    detected_time=None,
    contains_xbrl=None,
    document_type=None,
    filename=None,
    sequence=None,
    api_key=None,
    page=None,
    page_size=DEFAULT_PAGE_SIZE,
    quiet=False,
    include_metadata=False,
    filtered_accession_numbers=None,
    skip_accession_numbers=None,
    **metadata_filters,
):
    filters = _build_filters(
        cik=cik,
        ticker=ticker,
        accession=accession,
        submission_type=submission_type,
        filing_date=filing_date,
        report_date=report_date,
        detected_time=detected_time,
        contains_xbrl=contains_xbrl,
        document_type=document_type,
        filename=filename,
        sequence=sequence,
        **metadata_filters,
    )
    return _lookup_archive(
        "sgml-lookup",
        api_key=api_key,
        page=page,
        page_size=page_size,
        quiet=quiet,
        include_metadata=include_metadata,
        filtered_accession_numbers=filtered_accession_numbers,
        skip_accession_numbers=skip_accession_numbers,
        **filters,
    )


def lookup_archive_tar(
    cik=None,
    ticker=None,
    accession=None,
    submission_type=None,
    filing_date=None,
    report_date=None,
    detected_time=None,
    contains_xbrl=None,
    document_type=None,
    filename=None,
    sequence=None,
    api_key=None,
    page=None,
    page_size=DEFAULT_PAGE_SIZE,
    quiet=False,
    include_metadata=False,
    filtered_accession_numbers=None,
    skip_accession_numbers=None,
    **metadata_filters,
):
    filters = _build_filters(
        cik=cik,
        ticker=ticker,
        accession=accession,
        submission_type=submission_type,
        filing_date=filing_date,
        report_date=report_date,
        detected_time=detected_time,
        contains_xbrl=contains_xbrl,
        document_type=document_type,
        filename=filename,
        sequence=sequence,
        **metadata_filters,
    )
    return _lookup_archive(
        "tar-lookup",
        api_key=api_key,
        page=page,
        page_size=page_size,
        quiet=quiet,
        include_metadata=include_metadata,
        filtered_accession_numbers=filtered_accession_numbers,
        skip_accession_numbers=skip_accession_numbers,
        **filters,
    )
