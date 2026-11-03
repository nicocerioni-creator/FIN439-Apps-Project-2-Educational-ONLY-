"""Lab 18: live SEC numbers, reusable investing skill, and bring-your-own-AI memos."""
from pathlib import Path
import io
import json
import os
import sys
import zipfile

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SKILL = ROOT / '.agents' / 'skills' / 'buffett-business-review'
sys.path.insert(0, str(SKILL / 'scripts'))
from edgar import DEFAULT_AGENT, LABELS, SECClient, build_report, memo_packet, normalize_ticker, report_markdown
from memo_validation import audit_memo

st.set_page_config(page_title='Buffett business review | Lab 18', page_icon=':material/account_balance:', layout='wide')
st.title('Buffett business review')
st.caption('data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.')
st.markdown('Study the business. Audit the numbers. Make the judgment explicit.')


@st.cache_data(ttl=3600, max_entries=30, show_spinner=False)
def load_live(ticker, agent):
    return build_report(ticker, SECClient(agent))


def packet_zip(report):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('report.json', json.dumps(report, indent=2))
        archive.writestr('script_output.md', report_markdown(report))
        archive.writestr('memo_packet.md', memo_packet(report))
        for file in SKILL.rglob('*'):
            if file.is_file() and '__pycache__' not in file.parts and file.suffix in ('.py', '.md', '.yaml'):
                archive.write(file, 'buffett-business-review/' + str(file.relative_to(SKILL)))
    return buffer.getvalue()


with st.sidebar:
    st.header('Company research')
    source = st.segmented_control('Data source', ['Included example', 'Live SEC'], default='Included example')
    st.caption('Included examples: AAPL and COST.')
    with st.form('research'):
        ticker_input = st.text_input('Ticker', 'AAPL', max_chars=12)
        contact = st.text_input('SEC contact name and email', os.environ.get('SEC_USER_AGENT', DEFAULT_AGENT),
                                help='Identifies the downloader to SEC. This is not an API key. Forks can use their own contact.')
        submitted = st.form_submit_button('Load company', type='primary', width='stretch')
    st.caption('No API keys. No paid AI calls. A fresh memo is written in the AI tool you choose.')
    st.caption('Only US GAAP USD facts in 10-K filings enter the calculations. 10-Qs provide qualitative context only.')

if 'report' not in st.session_state:
    st.session_state.report = json.loads((ROOT / 'examples' / 'AAPL_report.json').read_text())
    st.session_state.loaded_source = 'Included example'
if submitted:
    try:
        ticker = normalize_ticker(ticker_input)
        if source == 'Included example':
            path = ROOT / 'examples' / f'{ticker}_report.json'
            if not path.exists():
                raise ValueError('Included examples are AAPL and COST. Choose Live SEC for another ticker.')
            report = json.loads(path.read_text())
        else:
            with st.spinner('Fetching SEC financial facts and filing passages…'):
                report = load_live(ticker, contact)
        st.session_state.report = report
        st.session_state.loaded_source = source
    except (ValueError, OSError, KeyError) as exc:
        st.error(str(exc))
        st.info('The last successfully loaded company remains below; its ticker and source are shown explicitly.')

report = st.session_state.report
st.subheader(f"{report['ticker']} · {report['company']}")
st.caption(f"{st.session_state.loaded_source} · retrieved {report['retrieved_at']} · annual facts in USD")
if st.session_state.loaded_source == 'Included example':
    st.info('This is a saved SEC snapshot for easy grading. Select Live SEC and load the company to refresh it.')
for warning in report.get('warnings', []):
    st.warning(warning)

with st.container(border=True):
    st.subheader('Earnings that reach the owners')
    chart_rows = []
    for row in report['rows']:
        for key in ('owner_earnings', 'net_income'):
            chart_rows.append({'Fiscal year end': row['fiscal_year_end'], 'Metric': LABELS[key],
                               'USD': row['metrics'][key]['value']})
    chart = alt.Chart(pd.DataFrame(chart_rows)).mark_line(point=True).encode(
        x=alt.X('Fiscal year end:O', sort=sorted(r['fiscal_year_end'] for r in report['rows'])),
        y=alt.Y('USD:Q', title='USD', axis=alt.Axis(format='~s')),
        color=alt.Color('Metric:N', scale=alt.Scale(range=['#426b91', '#b88746'])),
        tooltip=['Fiscal year end:O', 'Metric:N', alt.Tooltip('USD:Q', format=',.0f')]
    ).properties(height=320)
    st.altair_chart(chart, width='stretch', alt='Annual owner earnings proxy and net income, labelled by fiscal year end; missing values are gaps.')
    st.caption('Owner earnings proxy = operating cash flow − total capital spending. Missing values are gaps, never zeros or estimates.')

st.subheader('The three checks')
for label, result in report['checks'].items():
    with st.container(border=True):
        st.markdown(f'**{label}** — {result}')
st.caption('These are your specified Buffett-inspired checks, not a complete investment decision. ROE uses year-end equity. A nonpositive equity balance makes ROE not known.')

st.subheader('Annual financial table')
keys = ['revenue', 'net_income', 'operating_cash_flow', 'capital_spending', 'equity', 'roe', 'owner_earnings']
table = [{'Fiscal year end': r['fiscal_year_end'], **{LABELS[k]: r['metrics'][k]['display'] for k in keys}} for r in report['rows']]
st.dataframe(pd.DataFrame(table), hide_index=True, alt='Annual SEC financial metrics, ROE in percent and all other values in USD.')
with st.expander('XBRL tags, filing dates, and calculation provenance'):
    provenance = []
    for row in report['rows']:
        for key, cell in row['metrics'].items():
            provenance.append({'Fiscal year end': row['fiscal_year_end'], 'Metric': LABELS[key],
                               'Value': cell['display'], 'Tag or calculation': cell['tag'],
                               'Sources': '; '.join(f"{s['accession']} | {s.get('start') or 'instant'} → {s['end']} | filed {s['filed']}" for s in cell['sources'])})
    st.dataframe(pd.DataFrame(provenance), hide_index=True, alt='XBRL source tags, annual intervals, accession numbers and filing dates for every value.')
    st.caption('Latest eligible 10-K filing wins for each metric and fiscal period. Within that filing, the preferred tag wins. Annual flows span 364, 365, 366, or 371 inclusive days to allow calendar and 52/53-week fiscal years. Amendments and transition periods are excluded.')
    st.markdown(f"[SEC company facts]({report['facts_url']})")

with st.expander('Read the qualitative filing evidence'):
    for item in report.get('evidence', []):
        st.markdown(f"[{item['form']} · filed {item['filed']}]({item['url']})")
        for passage in item.get('passages', []):
            st.text(passage)
    st.caption('Automatically selected excerpts are limited evidence. Read the full linked filings before judging moat, management, or business durability.')

st.subheader('Generate your own fresh AI memo')
st.markdown('''The app prepares the evidence; your chosen AI writes the judgment. No credentials are entered here.

- Download the memo packet below.
- Open `memo_packet.md` in a text editor and paste its full contents into an AI chat, or attach that file if your AI supports files. Use your own account under its terms and usage limits; this app does not charge for AI generation.
- Ask the AI to return Markdown and include `Decision: own the business`, `Decision: watch it`, or `Decision: pass` on its own line. Keep the snapshot line unchanged.
- Save the response as a `.md` file and upload it below, or paste the Markdown. The app flags unsupported numbers and checks the snapshot and citation URLs.

If your AI supports Codex skills, the ZIP also includes `buffett-business-review`. Install it in your AI’s skills directory and invoke `$buffett-business-review` for a ticker.''')
st.download_button('Download memo packet and skill', packet_zip(report), file_name=f"{report['ticker']}_memo_packet.zip", mime='application/zip', width='stretch')
st.download_button('Download prompt only', memo_packet(report), file_name=f"{report['ticker']}_memo_packet.md", mime='text/markdown')
st.download_button('Download script output', report_markdown(report), file_name=f"{report['ticker']}_script_output.md", mime='text/markdown')

st.subheader('Memo and number audit')
memo_mode = st.segmented_control('Memo source', ['Saved example', 'Upload Markdown', 'Paste Markdown'], default='Saved example')
memo = ''
if memo_mode == 'Saved example':
    path = ROOT / 'examples' / f"{report['ticker']}_memo.md"
    if path.exists():
        memo = path.read_text()
    else:
        st.info('No saved memo exists for this ticker. Generate a fresh memo with the packet above.')
elif memo_mode == 'Upload Markdown':
    uploaded = st.file_uploader('Upload your AI memo', type=['md', 'txt'], max_upload_size=1, key='memo_upload_' + report['snapshot_id'])
    if uploaded:
        try:
            memo = uploaded.getvalue().decode('utf-8')
        except UnicodeDecodeError:
            st.error('Save the memo as UTF-8 text and upload again.')
else:
    memo = st.text_area('Paste your AI memo', height=280, max_chars=100_000, key='memo_paste_' + report['snapshot_id'])
if memo:
    audit = audit_memo(memo, report)
    if not audit['snapshot_match']:
        st.error('Snapshot missing or different. This memo is not verified against the currently displayed financial snapshot.')
    if not audit['decision_valid']:
        st.warning('Include exactly one decision line: Decision: own the business / watch it / pass.')
    if audit['flags']:
        st.error(f"{len(audit['flags'])} unsupported numerical occurrences found. Review every flagged occurrence below.")
        st.dataframe(pd.DataFrame(audit['flags']), hide_index=True, alt='Every unsupported numerical occurrence, its line number, and surrounding text.')
    else:
        st.success('No unsupported numerical occurrences detected.')
    if audit['unknown_citations']:
        st.warning('Citation URLs outside the supplied source list: ' + ', '.join(audit['unknown_citations']))
    st.caption('This is a conservative text check, not a factual endorsement. A printed number can still be assigned to the wrong metric, year, or company. URL identifiers, filing labels, snapshot IDs, and citation filing dates are metadata, not financial claims. Number words and abbreviated amounts are flagged for review.')
    with st.container(border=True):
        st.markdown(memo)
    st.download_button('Save memo as Markdown', memo, file_name=f"{report['ticker']}_memo.md", mime='text/markdown')

st.caption('For educational and research purposes only. Not investment or professional advice; no guarantee of future results. No market prices or valuation estimates are used.')
