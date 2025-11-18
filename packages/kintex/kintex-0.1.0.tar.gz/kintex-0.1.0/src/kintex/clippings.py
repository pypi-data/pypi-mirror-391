from __future__ import annotations

import re
import polars as pl
import hashlib

from difflib import SequenceMatcher
from datetime import datetime
from pathlib import Path
from typing import Any, NamedTuple, Iterator

from ._constants import CLIPPING_TYPES

__all__ = ["parse_clippings_to_dataframe"]


class ParsedClipping(NamedTuple):
    """Structured representation of a parsed clipping."""

    id: int
    uid: str  # unique, reproducible id based on title, author, timestamp, and content
    title: str
    author: str
    timestamp: datetime
    type: str
    loc_start: int | None
    loc_end: int | None
    page_start: int | None
    page_end: int | None
    content: str | None


INTERMEDIATE_SCHEMA = {
    "id": pl.Int32,
    "uid": pl.Utf8,
    "title": pl.Utf8,
    "author": pl.Utf8,
    "type": pl.Enum(CLIPPING_TYPES),
    "timestamp": pl.Datetime("us"),
    "loc_start": pl.Int32,
    "loc_end": pl.Int32,
    "page_start": pl.Int32,
    "page_end": pl.Int32,
    "content": pl.Utf8,
}

FINAL_SCHEMA = {
    "id": pl.Int32,
    "uid": pl.Utf8,
    "title": pl.Utf8,
    "author": pl.Utf8,
    "timestamp": pl.Datetime("us"),
    "loc_start": pl.Int32,
    "loc_end": pl.Int32,
    "page_start": pl.Int32,
    "page_end": pl.Int32,
    "highlight": pl.Utf8,
    "comment": pl.Utf8,
}


# Regex patterns for parsing
CLIPPING_SEPARATOR = "=========="
LOCATION_PATTERN = re.compile(r"location\s+(\d+)(?:-(\d+))?", re.IGNORECASE)
PAGE_PATTERN = re.compile(r"page\s*([ivxlcdm\d]+)(?:-([ivxlcdm\d]+))?", re.IGNORECASE)
TIMESTAMP_PATTERN = re.compile(r"added on (.+?)(?:\s*\||\s*$)", re.IGNORECASE)


def parse_clippings_to_dataframe(input_data: str | Path) -> pl.DataFrame:
    """
    Parse Kindle clippings text into a structured Polars DataFrame.

    Args:
        input_data: Either a file path or raw text string containing Kindle clippings

    Returns:
        Parsed clippings as a DataFrame

    Examples:
    """
    text = _load_text(input_data)
    snippets = _split_into_snippets(text)

    clipping_generator = _parse_snippets_to_records(snippets)
    records = list(clipping_generator)

    df = _create_dataframe(records)
    df = _remove_duplicates_from_dataframe(df)
    df = _merge_notes_with_highlights(df)

    return df


def _load_text(input_data: str | Path) -> str:
    """
    Load text from file path or return string input directly.

    Args:
        input_data: Either a file path or raw text string containing Kindle clippings

    Returns:
        Raw text content
    """
    if isinstance(input_data, Path):
        with open(input_data, "r", encoding="utf-8") as file:
            return file.read()
    elif isinstance(input_data, str):
        return input_data
    else:
        raise TypeError(f"Input must be string or Path, got {type(input_data)}")


def _split_into_snippets(text: str) -> list[str]:
    """
    Split clippings text into individual snippets.

    Args:
        text: Raw clippings text content

    Returns:
        List of individual snippets (excluding separators)
    """
    if not text or not text.strip():
        return []

    # Split by the clipping separator and filter out empty snippets
    snippets = []
    raw_snippets = text.split(CLIPPING_SEPARATOR)

    for snippet in raw_snippets:
        cleaned_snippet = snippet.strip()

        if not cleaned_snippet:
            continue

        # Split on a new line twice to separate title, metadata, and content (if it exists)
        # Filter out bookmarks and empty highlights/notes
        lines = [line.strip() for line in cleaned_snippet.split("\n", 2) if line.strip()]
        if len(lines) < 3:
            continue

        snippets.append(cleaned_snippet)

    return snippets


def _format_author_name(author: str) -> str:
    """
    Convert 'Surname, First' to 'First Surname' format.

    Args:
        author: Author name in various formats

    Returns:
        Standardized author name in 'First Surname' format
    """
    author = author.rstrip(")")

    author = (
        " ".join(part.strip() for part in reversed(author.split(",", 1)))
        if "," in author
        else author.strip()
    )

    return author


# TODO: refactor and simplify
# Create a new private function to handle multiple authors (with a list of patterns - &, and, ;)
def _parse_authors(author_string: str) -> list[str]:
    """
    Robust author parsing with multiple author handling strategies.

    Args:
        author_string: Raw author string from clipping title line

    Returns:
        List of standardized author names
    """
    if not author_string or not author_string.strip():
        return ""

    author_string = author_string.strip()

    # Handle common multi-author patterns
    if " & " in author_string:
        authors = author_string.split(" & ")
    elif " and " in author_string:
        authors = author_string.split(" and ")
    elif ";" in author_string:
        authors = author_string.split(";")
    elif author_string.count(",") > 1:  # Multiple commas suggest multiple authors
        # Handle "Surname1, First1, Surname2, First2" pattern
        parts = [p.strip() for p in author_string.split(",")]
        if len(parts) % 2 == 0:  # Even number suggests paired surname/first names
            authors = [f"{parts[i + 1]} {parts[i]}" for i in range(0, len(parts), 2)]
        else:
            authors = [author_string]  # Fallback to single author
    else:
        authors = [author_string]

    # Clean and format each author
    return "; ".join(_format_author_name(author.strip()) for author in authors if author.strip())


# TODO: refine to handle edge cases
def _parse_title_line(title_line: str) -> tuple[str, str]:
    """
    Extract book title and author from title line.

    Args:
        title_line: First line of snippet containing title and author info

    Returns:
        Tuple of (book_title, list_of_author)
    """
    # Remove byte order mark if present
    title_line = title_line.lstrip("\ufeff").strip()

    if title_line == "":
        raise ValueError("Title line is empty.")

    if "(" not in title_line or not title_line.endswith(")"):
        return title_line.strip(), ""

    title_str, author_str = title_line.rsplit("(", 1)
    title = title_str.strip()
    author = _parse_authors(author_str)
    return title, author


# TODO: preserve the roman numerals somehow?
def _parse_page(page):
    """
    Check the page is an integer, and return 0 if not.
    This is used to handle edge-cases where roman numerals are used for the page number.
    """
    try:
        return int(page)
    except ValueError:
        return 0


def _parse_metadata_line(metadata_line: str) -> dict:
    """
    Extract clipping metadata from the metadata line with robust parsing.

    Args:
        metadata_line: Second line of snippet containing metadata

    Returns:
        Dictionary with parsed metadata fields:
        - type: str ('highlight', 'note')
        - timestamp: datetime
        - loc_start: int | None
        - loc_end: int | None
        - page_start: int | None
        - page_end: int | None
    """
    metadata = {}

    metadata_lower = metadata_line.lower()
    if "highlight" in metadata_lower:
        metadata["type"] = "highlight"
    elif "note" in metadata_lower:
        metadata["type"] = "note"
    else:
        raise ValueError(f"Could not determine clipping type from metadata: {metadata_line}")

    loc_match = LOCATION_PATTERN.search(metadata_line)
    if loc_match:
        loc_start = int(loc_match.group(1))
        loc_end = int(loc_match.group(2)) if loc_match.group(2) else loc_start
        metadata["loc_start"] = loc_start
        metadata["loc_end"] = loc_end
    else:
        metadata["loc_start"] = None
        metadata["loc_end"] = None

    page_match = PAGE_PATTERN.search(metadata_line)

    if page_match:
        page_start = page_match.group(1)
        page_end = page_match.group(2) if page_match.group(2) else page_start
        metadata["page_start"] = _parse_page(page_start)
        metadata["page_end"] = _parse_page(page_end)
    else:
        metadata["page_start"] = None
        metadata["page_end"] = None

    timestamp_match = TIMESTAMP_PATTERN.search(metadata_line)
    if timestamp_match:
        timestamp_str = timestamp_match.group(1).strip()
        metadata["timestamp"] = _parse_timestamp(timestamp_str)
    else:
        raise ValueError(f"Could not find timestamp in metadata: {metadata_line}")

    return metadata


def _parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse timestamp string into datetime object.

    Args:
        timestamp_str: Raw timestamp string from metadata line

    Returns:
        Parsed datetime object
    """
    try:
        return datetime.strptime(timestamp_str, "%A, %d %B %Y %H:%M:%S")
    except ValueError:
        raise ValueError(f"Could not parse timestamp: {timestamp_str}")


def _parse_snippet(clipping_id: int, snippet: str) -> ParsedClipping | None:
    """
    Parse a single snippet with comprehensive error handling.

    Args:
        clipping_id: Sequential ID for this clipping
        snippet: Raw snippet text

    Returns:
        ParsedClipping instance or None if parsing fails
    """
    try:
        lines = [line.strip() for line in snippet.split("\n", 2) if line.strip()]

        title, author = _parse_title_line(lines[0])
        metadata = _parse_metadata_line(lines[1])
        content = lines[2] if len(lines) > 2 else None

        uid = generate_unique_id(title, author, metadata, content)

        clipping = ParsedClipping(
            id=clipping_id,
            uid=uid,
            title=title,
            author=author,
            type=metadata["type"],
            timestamp=metadata["timestamp"],
            loc_start=metadata["loc_start"],
            loc_end=metadata["loc_end"],
            page_start=metadata["page_start"],
            page_end=metadata["page_end"],
            content=content,
        )

        return clipping

    except Exception as e:
        print(f"Warning: Error parsing clipping {clipping_id}: {e}")
        return None


def generate_unique_id(title: str, author: str, metadata: dict[str, Any], content: str) -> str:
    """
    Create a unique, reproducible id for each parsed clipping, based on specific, unique details.
    This helps to identify and avoid processing/modifying clippings that already exist in a database.
    """
    normalized_title = title.strip()
    normalized_author = author.strip()
    normalized_timestamp = metadata["timestamp"].isoformat()
    normalized_content = content.strip()

    hash_input = (
        f"{normalized_title}|{normalized_author}|{normalized_timestamp}|{normalized_content}"
    )
    unique_id = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:16]

    return unique_id


def _parse_snippets_to_records(snippets: list[str]) -> Iterator[ParsedClipping]:
    """
    Generator that yields parsed clipping records with memory-efficient processing.

    Args:
        snippets: List of raw snippets

    Yields:
        ParsedClipping instances for successfully parsed clippings
    """
    total_snippets = len(snippets)
    successful_count = 0
    skipped_count = 0

    for i, snippet in enumerate(snippets):
        try:
            clipping = _parse_snippet(i, snippet)
            if clipping is not None:
                successful_count += 1
                yield clipping
            else:
                skipped_count += 1

        except Exception as e:
            skipped_count += 1
            print(f"Error processing clipping {i}: {e}")

    print(
        f"Parsing complete: {successful_count} successful, {skipped_count} skipped, {total_snippets} total"
    )


def _create_dataframe(records: list[ParsedClipping]) -> pl.DataFrame:
    """
    Create DataFrame from parsed clipping records.

    Args:
        records: List of ParsedClipping instances

    Returns:
        Polars DataFrame with intermediate schema
    """
    if not records:
        return pl.DataFrame(schema=INTERMEDIATE_SCHEMA)

    data = []
    for record in records:
        data.append(
            {
                "id": record.id,
                "uid": record.uid,
                "title": record.title,
                "author": record.author,
                "type": record.type,
                "timestamp": record.timestamp,
                "loc_start": record.loc_start,
                "loc_end": record.loc_end,
                "page_start": record.page_start,
                "page_end": record.page_end,
                "content": record.content,
            }
        )

    df = pl.DataFrame(data, schema=INTERMEDIATE_SCHEMA)

    return df


def _merge_notes_with_highlights(df: pl.DataFrame) -> pl.DataFrame:
    """
    Merge notes with their corresponding highlights based on location.

    This function implements a multi-stage matching algorithm:
    1. Location-based matching (notes within highlight ranges)
    2. Page-based fallback matching
    3. Handle orphaned records

    Args:
        df: DataFrame from parse_clippings_to_records with intermediate schema

    Returns:
        DataFrame with final merged schema containing highlight/comment pairs
    """
    if df.is_empty():
        return pl.DataFrame(schema=FINAL_SCHEMA)

    # Separate clippings by type for processing
    highlights_df = df.filter(pl.col("type") == "highlight")
    notes_df = df.filter(pl.col("type") == "note")

    merged_records = []
    merge_stats = {
        "location_matches": 0,
        "page_matches": 0,
        "orphaned_highlights": 0,
        "orphaned_notes": 0,
    }

    # Process each book separately for efficient matching
    books = df.select(["title", "author"]).unique()

    for book_row in books.iter_rows(named=True):
        book_title = book_row["title"]
        book_author = book_row["author"]

        # Get clippings for this specific book
        book_filter = (pl.col("title") == book_title) & (pl.col("author") == book_author)

        book_highlights = highlights_df.filter(book_filter)
        book_notes = notes_df.filter(book_filter)

        # Convert to lists for easier processing
        highlights_list = book_highlights.to_dicts()
        notes_list = book_notes.to_dicts()

        # Track which records have been matched
        matched_highlight_ids = set()
        matched_note_ids = set()

        # TODO: could be done more efficiently by filtering df for rows (note or highlight) where the loc_start or loc_end are NOT unique
        # Can then also keep as df, rather than a list of dicts
        # Stage 1: Location-based matching
        for note in notes_list:
            if note["id"] in matched_note_ids:
                continue

            for highlight in highlights_list:
                if highlight["id"] in matched_highlight_ids:
                    continue

                if _location_match(highlight, note):
                    merged_record = _create_merged_record(
                        highlight, note, "location", highlight["id"], highlight["uid"]
                    )
                    merged_records.append(merged_record)
                    matched_highlight_ids.add(highlight["id"])
                    matched_note_ids.add(note["id"])
                    merge_stats["location_matches"] += 1
                    break

        # # Stage 2: Page-based matching
        # for highlight in highlights_list:
        #     if highlight["id"] in matched_highlight_ids:
        #         continue

        #     for note in notes_list:
        #         if note["id"] in matched_note_ids:
        #             continue

        #         if _page_based_match(highlight, note):
        #             merged_record = _create_merged_record(
        #                 highlight, note, "page_based", highlight["id"]
        #             )
        #             merged_records.append(merged_record)
        #             matched_highlight_ids.add(highlight["id"])
        #             matched_note_ids.add(note["id"])
        #             merge_stats["page_matches"] += 1
        #             break

        for highlight in highlights_list:
            if highlight["id"] not in matched_highlight_ids:
                merged_record = _create_orphaned_highlight_record(
                    highlight, highlight["id"], highlight["uid"]
                )
                merged_records.append(merged_record)
                merge_stats["orphaned_highlights"] += 1

        for note in notes_list:
            if note["id"] not in matched_note_ids:
                merged_record = _create_orphaned_note_record(note, note["id"], note["uid"])
                merged_records.append(merged_record)
                merge_stats["orphaned_notes"] += 1

    if not merged_records:
        return pl.DataFrame(schema=FINAL_SCHEMA)

    final_df = pl.DataFrame(merged_records, FINAL_SCHEMA).sort(by="id")

    total_input = len(df)
    total_output = len(final_df)
    print("\nMerge Statistics:")
    print(f"  Input records: {total_input}")
    print(f"  Output records: {total_output}")
    print(f"  Location matches: {merge_stats['location_matches']}")
    print(f"  Page-based matches: {merge_stats['page_matches']}")
    print(f"  Orphaned highlights: {merge_stats['orphaned_highlights']}")
    print(f"  Orphaned notes: {merge_stats['orphaned_notes']}")

    return final_df


def _location_match(highlight: dict, note: dict) -> bool:
    """
    Check if note location falls within highlight range.

    Args:
        highlight: Highlight record dictionary
        note: Note record dictionary

    Returns:
        True if note location is within highlight range
    """
    if (
        highlight["loc_start"] is None
        or highlight["loc_end"] is None
        or note["loc_start"] is None
        or note["loc_end"] is None
    ):
        return False

    return note["loc_start"] >= highlight["loc_start"] and note["loc_end"] <= highlight["loc_end"]


def _page_based_match(highlight: dict, note: dict) -> bool:
    """
    Check if highlight and note are on the same page.

    Args:
        highlight: Highlight record dictionary
        note: Note record dictionary

    Returns:
        True if they share the same page
    """
    # Both must have page data
    if highlight["page_start"] is None or note["page_start"] is None:
        return False

    # For simplicity, check if start pages match
    # More sophisticated logic could handle page ranges
    return highlight["page_start"] == note["page_start"]


def _create_merged_record(
    highlight: dict, note: dict, merge_type: str, merged_id: int, merged_uid: int
) -> dict:
    """
    Create a merged record from a highlight and note pair.

    Args:
        highlight: Highlight record dictionary
        note: Note record dictionary
        merge_type: Type of merge performed
        merged_id: New ID for merged record

    Returns:
        Dictionary representing merged record
    """
    return {
        "id": merged_id,
        "uid": merged_uid,
        "title": highlight["title"],
        "author": highlight["author"],
        "timestamp": highlight["timestamp"],  # Use highlight timestamp as primary
        "loc_start": highlight["loc_start"],
        "loc_end": highlight["loc_end"],
        "page_start": highlight["page_start"],
        "page_end": highlight["page_end"],
        "highlight": highlight["content"],
        "comment": note["content"],
    }


def _create_orphaned_highlight_record(highlight: dict, merged_id: int, merged_uid: int) -> dict:
    """
    Create a record for an orphaned highlight (no matching note).

    Args:
        highlight: Highlight record dictionary
        merged_id: New ID for merged record

    Returns:
        Dictionary representing orphaned highlight record
    """
    return {
        "id": merged_id,
        "uid": merged_uid,
        "title": highlight["title"],
        "author": highlight["author"],
        "timestamp": highlight["timestamp"],
        "loc_start": highlight["loc_start"],
        "loc_end": highlight["loc_end"],
        "page_start": highlight["page_start"],
        "page_end": highlight["page_end"],
        "highlight": highlight["content"],
        "comment": None,
    }


def _create_orphaned_note_record(note: dict, merged_id: int, merged_uid: int) -> dict:
    """
    Create a record for an orphaned note (no matching highlight).

    Args:
        note: Note record dictionary
        merged_id: New ID for merged record

    Returns:
        Dictionary representing orphaned note record
    """
    return {
        "id": merged_id,
        "uid": merged_uid,
        "title": note["title"],
        "author": note["author"],
        "timestamp": note["timestamp"],
        "loc_start": note["loc_start"],
        "loc_end": note["loc_end"],
        "page_start": note["page_start"],
        "page_end": note["page_end"],
        "highlight": None,
        "comment": note["content"],
    }


# TODO: include option/flag parameter to see which duplicates were dropped
def _remove_duplicates_from_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    """
    Identifies duplicate notes or highlights from the same book, and removes them.

    Duplicates are identified where multiple notes or highlights have overlap in location (or page)
    and there is overlap in the content. This is due to the way the "My Clippings.txt" file works,
    whereby if you edit a highlight (or note), a new entry is recorded. This function is designed to
    identify those specific cases, while preserving different snippets that have the same location.

    Args:
        df: DataFrame with intermediate schema containing parsed clipping records

    Returns:
        DataFrame with duplicates removed, maintaining original schema and structure
    """
    df_left = df.lazy().select(
        [
            pl.col("title"),
            pl.col("author"),
            pl.col("type"),
            pl.col("id").alias("id_left"),
            pl.col("uid").alias("uid_left"),
            pl.col("loc_start").alias("loc_start_left"),
            pl.col("loc_end").alias("loc_end_left"),
            pl.col("content").alias("content_left"),
        ]
    )

    df_right = df.lazy().select(
        [
            pl.col("title"),
            pl.col("author"),
            pl.col("type"),
            pl.col("id").alias("id_right"),
            pl.col("uid").alias("uid_right"),
            pl.col("loc_start").alias("loc_start_right"),
            pl.col("loc_end").alias("loc_end_right"),
            pl.col("content").alias("content_right"),
        ]
    )

    # Identify possible duplicates by performing a self-join (grouped by title, author and type) and
    # filtering for snippets with overlapping location
    potential_duplicates = (
        df_left.join(df_right, on=["title", "author", "type"], how="inner")
        .filter(
            (pl.col("id_left") < pl.col("id_right"))
            & (
                pl.max_horizontal("loc_start_left", "loc_start_right")
                <= pl.min_horizontal("loc_end_left", "loc_end_right")
            )
        )
        .collect()
    )

    # Check and filter potential duplicates by content similarity
    duplicate_pairs = (
        potential_duplicates.with_columns(
            [
                pl.struct(["content_left", "content_right"])
                .map_elements(
                    lambda x: _analyze_content_similarity(x["content_left"], x["content_right"]),
                    return_dtype=pl.Struct(
                        {
                            "similarity_score": pl.Float64,
                            "shared_sequence": pl.Utf8,
                            "has_sufficient_overlap": pl.Boolean,
                        }
                    ),
                )
                .alias("similarity_analysis")
            ]
        )
        .unnest("similarity_analysis")
        .filter(pl.col("has_sufficient_overlap"))
    )

    ids_to_drop = duplicate_pairs["id_left"].unique().to_list()
    filtered_df = df.filter(~pl.col("id").is_in(ids_to_drop))
    print(f"{len(ids_to_drop)} duplicate snippets dropped.")

    return filtered_df


def _analyze_content_similarity(content1: str, content2: str, min_sequence_length: int = 4) -> dict:
    """
    Analyze content similarity between two strings using contiguous word sequences.

    Returns:
        dict with similarity_score, shared_sequence, and has_sufficient_overlap
    """
    if not content1 or not content2:
        return {"similarity_score": 0.0, "shared_sequence": "", "has_sufficient_overlap": False}

    # Clean and tokenize content
    words1 = _clean_and_tokenize(content1)
    words2 = _clean_and_tokenize(content2)

    if len(words1) < min_sequence_length or len(words2) < min_sequence_length:
        return {"similarity_score": 0.0, "shared_sequence": "", "has_sufficient_overlap": False}

    # Find longest common contiguous sequence
    longest_sequence, sequence_length = _find_longest_common_sequence(words1, words2)

    # Calculate similarity score
    max_length = max(len(words1), len(words2))
    similarity_score = sequence_length / max_length if max_length > 0 else 0.0

    # Check if sequence is long enough
    has_sufficient_overlap = sequence_length >= min_sequence_length

    return {
        "similarity_score": similarity_score,
        "shared_sequence": " ".join(longest_sequence) if longest_sequence else "",
        "has_sufficient_overlap": has_sufficient_overlap,
    }


def _clean_and_tokenize(text: str) -> list[str]:
    """Clean text and split into words, removing punctuation and normalizing."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    words = [word.strip() for word in cleaned.split() if word.strip()]
    return words


def _find_longest_common_sequence(words1: list[str], words2: list[str]) -> tuple[list[str], int]:
    """
    Find the longest contiguous sequence of words that appears in both lists.

    Returns:
        Tuple of (longest_sequence_words, length)
    """
    matcher = SequenceMatcher(None, words1, words2)
    matching_blocks = matcher.get_matching_blocks()

    longest_block = max(matching_blocks, key=lambda x: x.size, default=None)

    if longest_block and longest_block.size > 0:
        start_idx = longest_block.a
        length = longest_block.size
        longest_sequence = words1[start_idx : start_idx + length]
        return longest_sequence, length

    return [], 0


def _analyze_content_similarity_by_type(content1: str, content2: str, snippet_type: str) -> dict:
    """Analyze similarity using different strategies for notes vs highlights."""
    if not content1 or not content2:
        return {"similarity_score": 0.0, "shared_sequence": "", "has_sufficient_overlap": False}

    if snippet_type == "note":
        return _analyze_note_similarity(content1, content2)
    else:
        return _analyze_highlight_similarity(content1, content2)


# TODO: improve handling similarity between notes
# Might be better filtering/editing notes differently - combine them if it's not an extension
def _analyze_note_similarity(content1: str, content2: str) -> dict:
    """Note similarity: containment, character-level, or word overlap."""
    c1, c2 = content1.strip(), content2.strip()

    # Strategy 1: Containment (extensions like ".verb >> .v" in ".verb >> .v\ncaer")
    shorter, longer = (c1, c2) if len(c1) < len(c2) else (c2, c1)
    if shorter.lower() in longer.lower() and len(shorter) >= 3:
        ratio = len(shorter) / len(longer)
        if ratio >= 0.5:
            return {
                "similarity_score": ratio,
                "shared_sequence": shorter,
                "has_sufficient_overlap": True,
            }

    # Strategy 2: Character similarity (corrections like ".pb" -> ".ph")
    char_sim = SequenceMatcher(None, c1.lower(), c2.lower()).ratio()
    min_sim = 0.8 if max(len(c1), len(c2)) <= 10 else 0.9
    if char_sim >= min_sim:
        return {
            "similarity_score": char_sim,
            "shared_sequence": c1[:3],
            "has_sufficient_overlap": True,
        }

    # Strategy 3: Word overlap for short notes (1-3 words)
    if len(c1.split()) <= 3 or len(c2.split()) <= 3:
        words1, words2 = set(c1.lower().split()), set(c2.lower().split())
        common = words1 & words2
        if len(common) > 0 and len(common) / len(words1 | words2) >= 0.5:
            return {
                "similarity_score": len(common) / len(words1 | words2),
                "shared_sequence": " ".join(common),
                "has_sufficient_overlap": True,
            }

    return {"similarity_score": 0.0, "shared_sequence": "", "has_sufficient_overlap": True}


def _analyze_highlight_similarity(content1: str, content2: str, min_words: int = 4) -> dict:
    """Highlight similarity: contiguous word sequences."""
    words1 = re.sub(r"[^\w\s]", " ", content1.lower()).split()
    words2 = re.sub(r"[^\w\s]", " ", content2.lower()).split()

    if len(words1) < min_words or len(words2) < min_words:
        return {"similarity_score": 0.0, "shared_sequence": "", "has_sufficient_overlap": False}

    # Find longest common sequence
    matcher = SequenceMatcher(None, words1, words2)
    blocks = matcher.get_matching_blocks()
    longest = max(blocks, key=lambda x: x.size, default=None)

    if longest and longest.size >= min_words:
        sequence = words1[longest.a : longest.a + longest.size]
        score = longest.size / max(len(words1), len(words2))
        return {
            "similarity_score": score,
            "shared_sequence": " ".join(sequence),
            "has_sufficient_overlap": True,
        }

    return {"similarity_score": 0.0, "shared_sequence": "", "has_sufficient_overlap": False}
