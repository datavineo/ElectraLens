import pdfplumber
import pandas as pd
import os
import re
from typing import List


def clean_row(row: dict) -> dict:
    # normalize keys and values - handle multiple variations of column names
    r = {}
    r['name'] = (row.get('name') or row.get('Name') or row.get('NAME') or '').strip()
    
    # Handle age - try multiple variations
    age = row.get('age') or row.get('Age') or row.get('AGE') or ''
    try:
        r['age'] = int(float(age)) if age else None
    except (ValueError, TypeError):
        r['age'] = None
    
    r['gender'] = (row.get('gender') or row.get('Gender') or row.get('GENDER') or '').strip()
    r['constituency'] = (row.get('constituency') or row.get('Constituency') or row.get('CONSTITUENCY') or '').strip()
    
    # Handle booth_no - try multiple variations including Booth No (with space)
    r['booth_no'] = (row.get('booth_no') or row.get('booth no') or row.get('Booth No') or 
                     row.get('Booth') or row.get('booth') or row.get('BOOTH') or '').strip()
    
    r['address'] = (row.get('address') or row.get('Address') or row.get('ADDRESS') or '').strip()
    return r


def process_uploaded_pdf(pdf_path: str) -> str:
    """Extract tables from PDF to a cleaned CSV. Returns CSV path."""
    # try pdfplumber
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            try:
                tables = page.extract_tables()
            except Exception:
                tables = None
            if not tables:
                continue
            for table in tables:
                # assume first row is header
                if len(table) < 2:
                    continue
                # Normalize header - lowercase and strip whitespace
                header = [c.strip().lower().replace(' ', '_') if c else '' for c in table[0]]
                for r in table[1:]:
                    if not any(r):
                        continue
                    # Create row with both original and normalized keys
                    row = {}
                    for i in range(min(len(header), len(r))):
                        key = header[i]
                        value = (r[i] or '').strip()
                        # Add with normalized key
                        row[key] = value
                        # Also add original variations for flexibility
                        if 'booth' in key and 'no' in key:
                            row['booth_no'] = value
                        elif key == 'booth':
                            row['booth_no'] = value
                    rows.append(clean_row(row))

    print(f"📄 PDF Extraction Summary:")
    print(f"   Raw rows extracted: {len(rows)}")

    if not rows:
        # fallback: try tabula-py (requires java)
        try:
            import tabula
            df = tabula.read_pdf(pdf_path, pages='all', multiple_tables=False)
            if isinstance(df, list):
                df = pd.concat(df, ignore_index=True)
            rows = df.to_dict(orient='records')
            rows = [clean_row(r) for r in rows]
            print(f"   Rows extracted via tabula: {len(rows)}")
        except Exception as e:
            print(f"   Tabula extraction failed: {e}")
            pass

    # dedupe
    seen = set()
    cleaned = []
    for r in rows:
        key = (r.get('name','').lower(), r.get('constituency','').lower(), r.get('booth_no',''))
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(r)

    print(f"   After deduplication: {len(cleaned)} unique records")

    df = pd.DataFrame(cleaned)
    # ensure columns
    for c in ['name','age','gender','constituency','booth_no','address','vote']:
        if c not in df.columns:
            df[c] = None

    csv_path = os.path.splitext(pdf_path)[0] + '.csv'
    df.to_csv(csv_path, index=False)
    print(f"   CSV saved: {csv_path}")
    return csv_path


def load_csv_into_db(csv_path: str, db):
    import csv
    from app import models
    
    total_rows = 0
    duplicates_skipped = 0
    inserted = 0
    
    # read CSV and insert rows, skipping duplicates by same name+constituency+booth
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            total_rows += 1
            cr = clean_row(r)
            exists = db.query(models.Voter).filter(
                models.Voter.name == cr['name'],
                models.Voter.constituency == cr['constituency'],
                models.Voter.booth_no == cr['booth_no']
            ).first()
            if exists:
                duplicates_skipped += 1
                continue
            v = models.Voter(
                name=cr['name'] or 'UNKNOWN',
                age=cr['age'],
                gender=cr['gender'],
                constituency=cr['constituency'],
                booth_no=cr['booth_no'],
                address=cr['address'],
            )
            db.add(v)
            inserted += 1
        db.commit()
    
    print(f"✅ CSV Import Summary:")
    print(f"   Total rows in CSV: {total_rows}")
    print(f"   Duplicates skipped: {duplicates_skipped}")
    print(f"   New records inserted: {inserted}")
