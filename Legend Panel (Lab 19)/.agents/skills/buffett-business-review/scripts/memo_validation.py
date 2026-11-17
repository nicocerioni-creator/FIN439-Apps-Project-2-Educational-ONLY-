"""Conservative lexical number audit; this does not validate the meaning of a claim."""
import re

NUMBER = re.compile(r'\d{4}-\d{2}-\d{2}|[−+-]?\$?\d[\d,]*(?:\.\d+)?(?:[eE][+-]?\d+)?(?:\s?%|\s?(?:billion|million|trillion|thousand)\b|[bBmMkK]\b)?')
WORDS = re.compile(r'\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|trillion)\b', re.I)
URL = re.compile(r'https?://[^\s)>\]]+')


def tokens(text):
    return [m.group() for m in NUMBER.finditer(text)]


def normalize(token):
    return token.replace(',', '').replace('$', '').replace('−', '-').replace(' ', '').lstrip('+')


def audit_memo(memo, report):
    allowed = {normalize('15%')}
    for row in report['rows']:
        allowed.add(row['fiscal_year_end'])
        for cell in row['metrics'].values():
            # Only human-facing printed financial values, not arbitrary JSON identifiers.
            allowed.update(normalize(t) for t in tokens(cell['display']))
    text = memo
    # Keep character offsets stable while suppressing citation metadata and snapshot hashes.
    spans = [(m.start(), m.end()) for m in URL.finditer(text)]
    spans += [(m.start(), m.end()) for m in re.finditer(r'\b10-[KQ]\b', text)]
    spans += [(m.start(), m.end()) for m in re.finditer(r'^Snapshot:.*$', text, re.M)]
    # Citation filing dates are metadata only when attached to a recognized filing label.
    filing_dates = {e['filed'] for e in report.get('evidence', [])}
    filing_dates.update(s['filed'] for r in report['rows'] for c in r['metrics'].values() for s in c['sources'])
    spans += [(m.start(), m.end()) for m in re.finditer(r'(?<=filed )\d{4}-\d{2}-\d{2}', text) if m.group() in filing_dates]
    chars = list(text)
    for start, end in spans:
        chars[start:end] = ' ' * (end - start)
    visible = ''.join(chars)
    flags = []
    numeric_matches = list(NUMBER.finditer(visible))
    word_matches = [w for w in WORDS.finditer(visible) if not any(n.start() <= w.start() < n.end() for n in numeric_matches)]
    matches = sorted(numeric_matches + word_matches, key=lambda m: m.start())
    for m in matches:
        if normalize(m.group()) in allowed:
            continue
        flags.append({'number': m.group(), 'line': memo[:m.start()].count('\n') + 1,
                      'context': memo[max(0, m.start()-45):min(len(memo), m.end()+55)].replace('\n', ' ')})
    source_urls = {e['url'] for e in report.get('evidence', [])}
    source_urls.update(s['url'] for r in report['rows'] for c in r['metrics'].values() for s in c['sources'])
    urls = {m.group().rstrip('.,;') for m in URL.finditer(memo)}
    unknown_urls = sorted(urls - source_urls)
    snapshot_match = bool(re.search(r'^Snapshot:\s*`?' + re.escape(report['snapshot_id']) + r'`?\s*$', memo, re.M))
    verdicts = re.findall(r'^Decision:\s*(own the business|watch it|pass)\s*$', memo, re.I | re.M)
    return {'flags': flags, 'unknown_citations': unknown_urls, 'snapshot_match': snapshot_match,
            'decision_valid': len(verdicts) == 1, 'decision': verdicts[0].lower() if len(verdicts) == 1 else None}


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('memo', type=Path)
    args = parser.parse_args()
    result = audit_memo(args.memo.read_text(encoding='utf-8'), json.loads(args.report.read_text(encoding='utf-8')))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['snapshot_match'] and result['decision_valid'] and not result['flags'] and not result['unknown_citations'] else 1)
