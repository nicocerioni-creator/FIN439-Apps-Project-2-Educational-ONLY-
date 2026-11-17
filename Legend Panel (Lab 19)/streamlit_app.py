"""Lab 19: a public, keyless panel with a shared, auditable evidence contract."""
from pathlib import Path
import json
import os
import pandas as pd
import streamlit as st
from panel import (INVESTORS, ROOT, RESPONSIBILITY, agreement_text, build_report, edgar,
                   export_zip, memo_packet, panel_table, report_markdown, synthesize)

REPO = 'https://github.com/nicocerioni-creator/FIN439-Apps-Project-2-Educational-ONLY-'
st.set_page_config(page_title='Legend panel | Lab 19', page_icon=':material/groups:', layout='wide')
st.title('Legend panel')
st.markdown('**The same facts. Different philosophies. Your judgment.**')
st.caption('Buffett · Wood · Burry | Educational AI interpretations, not statements by the real investors.')


@st.cache_data(ttl=3600, max_entries=20, show_spinner=False)
def load_live(ticker, contact):
    return build_report(ticker, edgar.SECClient(contact))


with st.sidebar:
    st.header('Research settings')
    source = st.segmented_control('Data source', ['Included COST example', 'Live SEC'],
                                  default='Included COST example', required=True)
    with st.form('company'):
        ticker_input = st.text_input('Ticker', 'COST', max_chars=12)
        contact = st.text_input('SEC contact name and email', os.environ.get('SEC_USER_AGENT', edgar.DEFAULT_AGENT),
                                help='A public SEC downloader contact, not an API key. Forks should use their own contact.')
        submitted = st.form_submit_button('Load company', type='primary', width='stretch')
    st.caption('No AI API integration or API keys. The saved COST panel opens without network access.')
    st.link_button('View GitHub project', REPO + '/tree/main/Legend%20Panel%20%28Lab%2019%29', width='stretch')

if 'panel_report' not in st.session_state:
    st.session_state.panel_report = json.loads((ROOT / 'examples/COST_report.json').read_text())
    st.session_state.panel_source = 'Included COST example'
if submitted:
    try:
        ticker = edgar.normalize_ticker(ticker_input)
        if source == 'Included COST example':
            if ticker != 'COST':
                raise ValueError('Only COST is included. Choose Live SEC for other tickers.')
            loaded = json.loads((ROOT / 'examples/COST_report.json').read_text())
        else:
            with st.spinner('Loading annual SEC facts and filing excerpts…'):
                loaded = load_live(ticker, contact)
        st.session_state.panel_report = loaded
        st.session_state.panel_source = source
    except (ValueError, OSError, KeyError) as exc:
        st.error(str(exc))
        st.info('The last successfully loaded company remains below, with its source and snapshot shown.')

report = st.session_state.panel_report
st.subheader(f"{report['ticker']} · {report['company']}")
st.caption(f"{st.session_state.panel_source} · retrieved {report['retrieved_at']} · financial amounts in USD")
st.caption(f"Snapshot: {report['snapshot_id']}")
if st.session_state.panel_source == 'Included COST example':
    st.info('Saved SEC snapshot and AI-written memos. Use Live SEC to refresh; refreshed facts need matching fresh memos.')
for warning in report['warnings']:
    st.warning(warning)

st.subheader('Panel table · investor × check')
st.dataframe(pd.DataFrame(panel_table(report)), hide_index=True,
             alt='Investors and their coded checks. Pass, fail, and not known are written explicitly.')
st.caption('— means this check belongs to another investor. “Not known” means required evidence is unavailable. '
           'Checks use unrounded inputs; displayed ratios are rounded.')

latest = report['rows'][-1]['metrics']
with st.container(horizontal=True):
    st.metric('Revenue growth a year', report['summary']['revenue_cagr']['display'], border=True)
    st.metric('Latest R&D / revenue', latest['rd_intensity']['display'], border=True)
    st.metric('Latest liabilities / equity', latest['liabilities_to_equity']['display'], border=True)
st.caption('Revenue CAGR = (last revenue ÷ first revenue)^(1/4) − 1. Five annual observations span four intervals. '
           'Missing ResearchAndDevelopmentExpense means not found, never zero.')

st.subheader('Memos and verdicts · side by side')
mode = st.segmented_control('Memo source', ['Saved COST memos', 'Paste Markdown', 'Upload Markdown'],
                            default='Saved COST memos', required=True)
layout = st.segmented_control('Reading layout', ['Side by side', 'Stacked'], default='Side by side', required=True,
                              help='Stacked offers a wider reading area. Columns also stack on narrow screens.')
memos = {}
columns = st.columns(3, border=True) if layout == 'Side by side' else [st.container(border=True) for _ in INVESTORS]
for (key, name), column in zip(INVESTORS.items(), columns):
    with column:
        st.subheader(name)
        memo = ''
        identity = key + '_' + report['snapshot_id']
        if mode == 'Saved COST memos':
            path = ROOT / 'examples' / f"{report['ticker']}_{key}_memo.md"
            if path.exists():
                memo = path.read_text(encoding='utf-8')
        elif mode == 'Paste Markdown':
            memo = st.text_area(f'{name} memo Markdown', key='paste_' + identity, height=200, max_chars=100_000)
        else:
            uploaded = st.file_uploader(f'{name} memo Markdown', type=['md', 'txt'],
                                       key='upload_' + identity, max_upload_size=1)
            if uploaded:
                try:
                    memo = uploaded.getvalue().decode('utf-8')
                except UnicodeDecodeError:
                    st.error('Please save this memo as UTF-8 text.')
        memos[key] = memo
        individual = synthesize(report, {key: memo})['audits'][key]
        st.markdown('**Verdict:** ' + (individual['decision'] or 'not known'))
        if memo:
            if not individual['snapshot_match']:
                st.error('Snapshot missing or different: this memo does not match the displayed evidence.')
            if not individual['decision_valid']:
                st.error('Include exactly one valid Decision line.')
            if individual['flags']:
                st.error('Unprinted numbers detected; review the audit below.')
            if individual['unknown_citations']:
                st.error('Citation URLs outside the provided evidence: ' + ', '.join(individual['unknown_citations']))
            st.markdown(memo)
            st.download_button('Download this memo', memo, file_name=f"{report['ticker']}_{key}_memo.md", key='download_' + key)
        else:
            st.info('No memo loaded. Download this investor’s packet below and use your chosen AI chat.')

result = synthesize(report, memos)
st.subheader('One panel verdict · your final judgment')
with st.container(border=True):
    st.markdown(f"**Business-quality verdict: {result['decision']}**")
    st.markdown(result['rationale'])
    st.markdown('**Would I trust the panel?** ' + result['trust'])
    st.markdown('**' + RESPONSIBILITY + '**')
st.subheader('Where the philosophies agree and split')
st.markdown(agreement_text(report))
st.caption('The saved analyses were written by the same AI through separate skills. They are not independent '
           'human opinions, separate model votes, or current positions held by these investors.')

st.subheader('Unprinted-number flag · across all memos')
flags = [{'Investor': INVESTORS[k], **f} for k, a in result['audits'].items() for f in a['flags']]
if flags:
    st.error('FLAGGED: unsupported numerical occurrences found across the memos.')
    st.dataframe(pd.DataFrame(flags), hide_index=True, alt='Investor, number, line, and context for every unprinted numerical occurrence.')
elif all(memos.values()):
    st.success('CLEAR: no unprinted numerical occurrences detected across all memos.')
else:
    st.warning('INCOMPLETE: load every memo before treating the panel audit as complete.')
st.caption('The lexical audit accepts only printed values and thresholds. It cannot verify that a printed '
           'number was assigned to the correct metric/year, or that a citation supports a claim. '
           'Snapshot, decision, and citation problems also block the panel synthesis.')

st.subheader('Annual financial facts')
keys = ['revenue', 'net_income', 'operating_cash_flow', 'capital_spending', 'equity', 'liabilities',
        'research_and_development', 'owner_earnings', 'roe', 'rd_intensity', 'liabilities_to_equity']
edgar.LABELS['rd_intensity'] = 'R&D / revenue'
st.dataframe(pd.DataFrame([{'Fiscal year end': r['fiscal_year_end'], **{
    edgar.LABELS[k]: r['metrics'][k]['display'] for k in keys}} for r in report['rows']]),
    hide_index=True, alt='Annual financial facts in USD, ROE and R&D intensity in percent, and liabilities to equity as a ratio.')
st.caption('Owner earnings proxy = operating cash flow − total capital spending; this is not Buffett’s complete definition. '
           'ROE uses year-end equity. Only exact 10-K USD US-GAAP annual facts enter financial calculations.')

with st.expander('XBRL tags and source provenance'):
    provenance = [{'Fiscal year end': row['fiscal_year_end'], 'Metric': edgar.LABELS[k],
                   'Printed value': c['display'], 'Tag / calculation': c['tag'],
                   'Sources': '; '.join(f"{s['accession']} | {s.get('start') or 'instant'} → {s['end']} | filed {s['filed']} | {s['url']}" for s in c['sources'])}
                  for row in report['rows'] for k, c in row['metrics'].items()]
    st.dataframe(pd.DataFrame(provenance), hide_index=True, alt='Tags, reporting periods, filing dates, accession numbers, and SEC URLs for the financial facts.')
    st.markdown(f"[SEC company facts]({report['facts_url']})")
    st.caption('Latest eligible filing wins per metric/period. Preferred tags break ties within a filing. '
               'Annual intervals are 364, 365, 366, or 371 inclusive days. Amendments and partial years are excluded.')
with st.expander('Qualitative evidence · read the filings'):
    for item in report['evidence']:
        st.markdown(f"[{item['form']} filed {item['filed']}]({item['url']})")
        for passage in item['passages']:
            st.text(passage)
    st.caption('Automatically selected excerpts are incomplete. 10-Q passages provide qualitative context only.')

st.subheader('Refresh memos without an API key')
st.markdown('Download a separate packet for each investor. Give each packet to a fresh AI chat, '
            'without the other memos, and request its Markdown memo. Then paste or upload each response above. '
            'Keep its Snapshot line and exactly one Decision line. This app makes no model calls and cannot '
            'charge an owner’s AI account. Your chosen external AI service has its own terms and usage limits.')
for key, name in INVESTORS.items():
    st.download_button(f'Download {name} packet', memo_packet(report, key),
                       file_name=f"{report['ticker']}_{key}_memo_packet.md", mime='text/markdown')
st.download_button('Download full evidence, skills, memos and audit ZIP', export_zip(report, memos),
                   file_name=f"{report['ticker']}_panel.zip", mime='application/zip', width='stretch')
st.download_button('Download printed script output', report_markdown(report),
                   file_name=f"{report['ticker']}_script_output.md", mime='text/markdown')
st.caption('Uploads and pasted memos stay in the app session/process and are not committed or saved to the repository. '
           'For educational and research purposes only. Not investment or other professional advice. '
           'No guarantee of future results. No stock prices, valuations, forecasts, or holdings are assessed.')
