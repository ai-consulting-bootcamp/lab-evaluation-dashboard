"""Build the two Tableau workbooks as code (.twb XML, packaged into .twbx).

    evaluation_score_dashboard.twbx  - main lab: KPIs, histogram, scores by category,
                                       category comparison, 3 filters, click-to-filter
    judge_agreement_dashboard.twbx   - optional extra: agreement KPIs, agreement by
                                       category, disagreement histogram, judge scatter

Each .twbx is a zip holding the .twb plus a Hyper extract of its CSV under
Data/Datasources/, so it opens on any machine without re-pointing the data source.
Tableau Public refuses non-extract data sources, hence Hyper rather than the raw CSV.
Requires: pip install tableauhyperapi
"""
import os
import re
import tempfile
import zipfile
from xml.sax.saxutils import escape, quoteattr

# --------------------------------------------------------------------------- helpers


def q(s):
    """XML attribute value (with quotes)."""
    return quoteattr(s)


def text_run(text, **attrs):
    a = ''.join(f' {k.replace("_", "-")}={q(str(v))}' for k, v in attrs.items())
    return f'<run{a}>{escape(text)}</run>'


def column(name, datatype, role, typ, caption=None, formula=None, fmt=None):
    cap = f' caption={q(caption)}' if caption else ''
    df = f' default-format={q(fmt)}' if fmt else ''
    body = (f'<calculation class="tableau" formula={q(formula)} />' if formula else '')
    if body:
        return (f'<column{cap} datatype="{datatype}"{df} name="[{name}]" role="{role}" '
                f'type="{typ}">{body}</column>')
    return f'<column{cap} datatype="{datatype}"{df} name="[{name}]" role="{role}" type="{typ}" />'


HYPER_COLUMNS = {}   # csv name -> [(column, tableau datatype)], used by build_hyper()


def datasource(ds, caption, csv, raw_cols, extra_cols, palettes=()):
    """Connect to a Hyper extract of `csv`. Tableau Public only opens extract-based
    workbooks, so the CSV is converted to .hyper (table [Extract].[Extract]) at package time.
    raw_cols: [(name, datatype)] in file order; extra_cols: list of <column> xml.
    palettes: [(column-instance tuple, {value: hex colour})] - fixed colours per category."""
    HYPER_COLUMNS[csv] = raw_cols
    hyper = csv.replace('.csv', '.hyper')
    conn = f'hyper.{ds[10:]}'
    return f'''
    <datasource caption={q(caption)} inline="true" name="{ds}" version="18.1">
      <connection class="federated">
        <named-connections>
          <named-connection caption={q(caption)} name="{conn}">
            <connection authentication="auth-none" author-locale="en_US" class="hyper" dbname="Data/Datasources/{hyper}" default-settings="yes" port="" sslmode="" username="tableau_internal_user" />
          </named-connection>
        </named-connections>
        <relation connection="{conn}" name="Extract" table="[Extract].[Extract]" type="table" />
      </connection>
      <aliases enabled="yes" />
      {''.join(extra_cols)}
      {''.join(f'<column-instance column="[{c}]" derivation="{d}" name="[{n}]" pivot="key" type="{t}" />'
               for (c, d, n, t), _ in palettes)}
      <layout dim-ordering="alphabetic" dim-percentage="0.5" measure-ordering="alphabetic" measure-percentage="0.4" show-structure="true" />
      {palette_style(palettes)}
    </datasource>'''


def palette_style(palettes):
    """Categorical colour maps live on the data source, keyed by column-instance name."""
    if not palettes:
        return ''
    rules = ''.join(
        f'<encoding attr="color" field="[{inst[2]}]" type="palette">'
        + ''.join(f'<map to="{hex_}"><bucket>{escape(chr(34) + value + chr(34))}</bucket></map>'
                  for value, hex_ in colours.items())
        + '</encoding>' for inst, colours in palettes)
    return f'<style><style-rule element="mark">{rules}</style-rule></style>'


def build_hyper(csv, out_dir):
    """CSV -> Hyper extract with one table, [Extract].[Extract]."""
    from tableauhyperapi import (Connection, CreateMode, HyperProcess, SqlType, TableDefinition,
                                 TableName, Telemetry, escape_string_literal)
    types = {'integer': SqlType.big_int(), 'real': SqlType.double(),
             'string': SqlType.text(), 'date': SqlType.date()}
    hyper = os.path.join(out_dir, csv.replace('.csv', '.hyper'))
    table = TableDefinition(TableName('Extract', 'Extract'),
                            [TableDefinition.Column(n, types[t]) for n, t in HYPER_COLUMNS[csv]])
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,
                      parameters={'log_dir': out_dir}) as hp, \
            Connection(hp.endpoint, hyper, CreateMode.CREATE_AND_REPLACE) as c:
        c.catalog.create_schema('Extract')
        c.catalog.create_table(table)
        n = c.execute_command(f'COPY {table.table_name} FROM {escape_string_literal(csv)} '
                              f'WITH (format csv, header)')
    print(f'  extract: {os.path.basename(hyper)} ({n} rows)')
    return hyper


def deps(ds, cols, instances):
    """datasource-dependencies: cols = <column> xml list, instances = (col, derivation, name, type)."""
    inst = ''.join(f'<column-instance column="[{c}]" derivation="{d}" name="[{n}]" '
                   f'pivot="key" type="{t}" />' for c, d, n, t in instances)
    return f'<datasource-dependencies datasource="{ds}">{"".join(cols)}{inst}</datasource-dependencies>'


def cat_filter(ds, inst, group):
    return (f'<filter class="categorical" column="[{ds}].[{inst}]" filter-group="{group}">'
            f'<groupfilter function="level-members" level="[{inst}]" '
            f'user:ui-enumeration="all" user:ui-marker="enumerate" /></filter>')


def date_filter(ds, inst, group):
    return (f'<filter class="quantitative" column="[{ds}].[{inst}]" filter-group="{group}" '
            f'included-values="in-range" />')


def slices(filters):
    cols = re.findall(r'<filter class="\w+" column="([^"]+)"', filters)
    return '<slices>' + ''.join(f'<column>{c}</column>' for c in cols) + '</slices>' if cols else ''


def worksheet(name, ds, ds_caption, dependencies, rows='', cols='', mark='Bar',
              encodings='', filters='', sorts='', aggregated=True, pane_style='',
              table_style='', title=None, pane_extra=''):
    title_xml = ''
    if title:
        title_xml = (f'<layout-options><title><formatted-text>'
                     f'{text_run(title, bold="true", fontsize="12")}'
                     f'</formatted-text></title></layout-options>')
    return f'''
    <worksheet name={q(name)}>
      {title_xml}
      <table>
        <view>
          <datasources><datasource caption={q(ds_caption)} name="{ds}" /></datasources>
          {dependencies}
          {filters}
          {sorts}
          {slices(filters)}
          <aggregation value="{'true' if aggregated else 'false'}" />
        </view>
        <style>{table_style}</style>
        <panes>
          <pane selection-relaxation-option="selection-relaxation-allow">
            <view><breakdown value="auto" /></view>
            <mark class="{mark}" />
            <encodings>{encodings}</encodings>
            {pane_extra}
            <style>{pane_style}</style>
          </pane>
        </panes>
        <rows>{rows}</rows>
        <cols>{cols}</cols>
      </table>
    </worksheet>'''


def labels_on(extra=''):
    return f'<style-rule element="mark"><format attr="mark-labels-show" value="true" />{extra}</style-rule>'


def kpi_sheet(name, ds, ds_caption, dependencies, inst, caption, filters):
    label = (f'<customized-label><formatted-text>'
             f'{text_run(f"<[{ds}].[{inst}]>", bold="true", fontcolor="#1f3b57", fontsize="22")}'
             f'</formatted-text></customized-label>')
    cell = ('<style-rule element="cell"><format attr="width" value="420" />'
            '<format attr="height" value="60" /><format attr="text-align" value="center" /></style-rule>')
    return worksheet(name, ds, ds_caption, dependencies, mark='Text',
                     encodings=f'<text column="[{ds}].[{inst}]" />', filters=filters,
                     table_style=cell, title=caption,
                     pane_extra=label, pane_style=labels_on())


def zone(zid, x, y, w, h, **kw):
    attrs = ''.join(f' {k.replace("_", "-")}={q(str(v))}' for k, v in kw.items())
    return f'<zone h="{h}" id="{zid}" w="{w}" x="{x}" y="{y}"{attrs}'


def text_zone(zid, x, y, w, h, runs):
    return (zone(zid, x, y, w, h, type_v2='text') +
            f'><formatted-text>{"".join(runs)}</formatted-text>'
            f'<zone-style><format attr="margin" value="8" /></zone-style></zone>')


def sheet_zone(zid, x, y, w, h, name):
    return zone(zid, x, y, w, h, name=name) + (
        '><zone-style><format attr="border-color" value="#e0e0e0" />'
        '<format attr="border-style" value="solid" /><format attr="border-width" value="1" />'
        '<format attr="margin" value="4" /></zone-style></zone>')


def filter_zone(zid, x, y, w, h, sheet, param, mode):
    return zone(zid, x, y, w, h, name=sheet, param=param, type_v2='filter', mode=mode,
                values='database') + ' />'


def legend_zone(zid, x, y, w, h, sheet, param):
    return zone(zid, x, y, w, h, name=sheet, param=param, type_v2='color',
                pane_specification_id=0, leg_item_layout='vert') + ' />'


def filter_action(dashboard, source_sheet, caption, aid):
    return f'''
    <action caption={q(caption)} name="[Action{aid}]">
      <activation auto-clear="true" type="on-select" />
      <source dashboard={q(dashboard)} type="sheet" worksheet={q(source_sheet)} />
      <command command="tsc:tsl-filter">
        <param name="special-fields" value="all" />
        <param name="target" value={q(dashboard)} />
      </command>
    </action>'''


def dashboard(name, zones):
    return f'''
    <dashboard name={q(name)}>
      <style />
      <size sizing-mode="automatic" />
      <zones>
        <zone h="100000" id="1" type-v2="layout-basic" w="100000" x="0" y="0">
          {''.join(zones)}
        </zone>
      </zones>
    </dashboard>'''


def workbook(datasources, worksheets, dashboards, actions, windows):
    return f'''<?xml version='1.0' encoding='utf-8' ?>
<workbook original-version="18.1" source-build="0.0.0 (0000.25.1024.2150)" source-platform="mac" version="18.1" xmlns:user="http://www.tableausoftware.com/xml/user">
  <preferences>
    <preference name="ui.encoding.shelf.height" value="24" />
    <preference name="ui.shelf.height" value="26" />
  </preferences>
  <datasources>{datasources}</datasources>
  {f"<actions>{actions}</actions>" if actions else ""}
  <worksheets>{worksheets}</worksheets>
  <dashboards>{dashboards}</dashboards>
  <windows>{windows}</windows>
</workbook>
'''


def windows(dash_name, sheet_names):
    """Only the dashboard gets a window; sheets stay available as tabs."""
    vps = ''.join(f'<viewpoint name={q(s)}><zoom type="entire-view" /></viewpoint>' for s in sheet_names)
    return (f'<window class="dashboard" maximized="true" name={q(dash_name)}>'
            f'<viewpoints>{vps}</viewpoints><active id="-1" /></window>')


def package(twb_name, twb_xml, csv):
    """Zip the workbook XML and a Hyper extract of `csv` into a .twbx.
    The extract and Hyper's logs are built in a temp dir, so nothing else lands in the repo."""
    out = twb_name.replace('.twb', '.twbx')
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(twb_name, twb_xml)
        hyper = build_hyper(csv, tmp)
        z.write(hyper, f'Data/Datasources/{os.path.basename(hyper)}')
    print(f'wrote {out}')


# --------------------------------------------------------------------- evaluation book

DS = 'federated.0evalscores0000000000000000'
CAP = 'Evaluation scores'
DASH = 'Model Evaluation Score Dashboard'

C_CAT = column('category_label', 'string', 'dimension', 'nominal', caption='Category')
C_MODEL = column('model_version', 'string', 'dimension', 'nominal', caption='Model')
C_DATE = column('date', 'date', 'dimension', 'ordinal', caption='Date')
C_SCORE = column('score', 'real', 'measure', 'quantitative', caption='Score', fmt='n#,##0.0')
C_ID = column('evaluation_id', 'integer', 'dimension', 'ordinal', caption='Evaluation ID')
C_BAND = column('Calculation_band', 'string', 'dimension', 'nominal', caption='Score Band',
                formula='STR(MIN(INT([score]/10)*10, 90)) + "-" + '
                        'IIF(INT([score]/10)*10 >= 90, "100", STR(INT([score]/10)*10 + 9))')
C_PASS = column('Calculation_pass', 'real', 'measure', 'quantitative',
                caption='Share scoring 70+', fmt='p0%',
                formula='SUM(IIF([score] >= 70, 1, 0)) / COUNT([evaluation_id])')
C_AVG = column('Calculation_avg', 'real', 'measure', 'quantitative', caption='Average score',
               fmt='n#,##0.0', formula='AVG([score])')
C_N = column('Calculation_n', 'integer', 'measure', 'quantitative', caption='Number of answers',
             fmt='n#,##0', formula='COUNT([evaluation_id])')
C_STATUS = column('Calculation_status', 'string', 'measure', 'nominal', caption='Status',
                  formula='IF AVG([score]) >= 70 THEN "Strong (70+)" '
                          'ELSEIF AVG([score]) >= 50 THEN "Acceptable (50-69)" '
                          'ELSE "Needs improvement (under 50)" END')

I_CAT = ('category_label', 'None', 'none:category_label:nk', 'nominal')
I_MODEL = ('model_version', 'None', 'none:model_version:nk', 'nominal')
I_DATE = ('date', 'None', 'none:date:qk', 'quantitative')
I_AVG = ('Calculation_avg', 'User', 'usr:Calculation_avg:qk', 'quantitative')
I_SCORE = ('score', 'None', 'none:score:qk', 'quantitative')
I_CNT = ('Calculation_n', 'User', 'usr:Calculation_n:qk', 'quantitative')
I_BAND = ('Calculation_band', 'None', 'none:Calculation_band:nk', 'nominal')
I_PASS = ('Calculation_pass', 'User', 'usr:Calculation_pass:qk', 'quantitative')
I_STATUS = ('Calculation_status', 'User', 'usr:Calculation_status:nk', 'nominal')

FILTER_COLS = [C_CAT, C_MODEL, C_DATE]
FILTER_INST = [I_CAT, I_MODEL, I_DATE]
# filter-group links the same filter across every sheet ("apply to all worksheets")
FILTERS = (cat_filter(DS, 'none:model_version:nk', 2) +
           cat_filter(DS, 'none:category_label:nk', 3) +
           date_filter(DS, 'none:date:qk', 4))


def r(inst):  # shelf reference
    return f'[{DS}].[{inst}]'


def eval_book():
    ds_xml = datasource(DS, CAP, 'evaluation_data_clean.csv',
                        [('evaluation_id', 'integer'), ('category', 'string'),
                         ('category_label', 'string'), ('score', 'real'),
                         ('model_version', 'string'), ('date', 'date')],
                        [C_CAT, C_MODEL, C_DATE, C_SCORE, C_ID, C_BAND, C_PASS, C_AVG, C_N, C_STATUS],
                        palettes=[(I_STATUS, {'Strong (70+)': '#2e7d32', 'Acceptable (50-69)': '#f0a202',
                                              'Needs improvement (under 50)': '#c62828'})])
    sheets = []
    # KPI tiles
    for name, inst, cap, cols in [
        ('KPI Average', I_AVG, 'Average score (0-100)', [C_AVG, C_SCORE]),
        ('KPI Count', I_CNT, 'Answers evaluated', [C_N, C_ID]),
        ('KPI Pass', I_PASS, 'Share of answers scoring 70+', [C_PASS, C_SCORE, C_ID]),
    ]:
        sheets.append(kpi_sheet(name, DS, CAP, deps(DS, cols + FILTER_COLS, [inst] + FILTER_INST),
                                inst[2], cap, FILTERS))

    # 1. Category comparison: sorted bars, coloured by status, overall-average line
    sheets.append(worksheet(
        'Category Comparison', DS, CAP,
        deps(DS, [C_CAT, C_SCORE, C_AVG, C_STATUS] + FILTER_COLS[1:], [I_AVG, I_STATUS] + FILTER_INST),
        rows=r('none:category_label:nk'), cols=r('usr:Calculation_avg:qk'), mark='Bar',
        encodings=f'<color column="{r("usr:Calculation_status:nk")}" />',
        filters=FILTERS,
        sorts=f'<sort class="computed" column="{r("none:category_label:nk")}" direction="DESC" '
              f'using="{r("usr:Calculation_avg:qk")}" />',
        pane_style=labels_on(),
        title='Which task types does the model handle well? (average score, click a bar to filter)',
        pane_extra=f'<reference-line axis-column="{r("usr:Calculation_avg:qk")}" enable-instant-analytics="true" '
                    f'formula="average" id="refline0" label-type="automatic" scope="per-table" '
                    f'value-column="{r("usr:Calculation_avg:qk")}" z-order="1" />'))

    # 2. Score distribution histogram
    sheets.append(worksheet(
        'Score Distribution', DS, CAP,
        deps(DS, [C_BAND, C_ID, C_N] + FILTER_COLS, [I_BAND, I_CNT] + FILTER_INST),
        rows=r('usr:Calculation_n:qk'), cols=r('none:Calculation_band:nk'), mark='Bar',
        filters=FILTERS, pane_style=labels_on(),
        title='How are all scores spread? (number of answers per 10-point score band)'))

    # 3. Scores by category: every answer as a dot + box plot
    sheets.append(worksheet(
        'Scores by Category', DS, CAP,
        deps(DS, [C_CAT, C_SCORE] + FILTER_COLS[1:], [I_SCORE] + FILTER_INST),
        rows=r('none:score:qk'), cols=r('none:category_label:nk'), mark='Circle',
        filters=FILTERS, aggregated=False,
        pane_style='<style-rule element="mark"><format attr="mark-color" value="#4e79a7" />'
                   '<format attr="mark-transparency" value="50" /><format attr="size" value="0.25" /></style-rule>',
        title='How consistent is each task type? (each dot is one answer; box = middle half of scores)',
        pane_extra=f'<reference-line axis-column="{r("none:score:qk")}" boxplot-mark-exclusion="false" '
                    f'boxplot-whisker-type="standard" enable-instant-analytics="true" formula="average" '
                    f'id="refline1" label-type="automatic" scope="per-cell" '
                    f'value-column="{r("none:score:qk")}" z-order="2" />'))

    sheet_names = ['KPI Average', 'KPI Count', 'KPI Pass', 'Category Comparison',
                   'Score Distribution', 'Scores by Category']

    zones = [
        text_zone(3, 0, 0, 100000, 12000, [
            text_run('Model Evaluation Score Dashboard\n', bold='true', fontsize='20', fontcolor='#1f3b57'),
            text_run('How well our AI models answer, by task type. Scores run from 0 to 100, where 100 is a '
                     'perfect answer. Data: 4,489 evaluated answers, 28 Aug - 25 Nov 2026. '
                     'Use the filters on the right, or click a category bar, to drill down.',
                     fontsize='11', fontcolor='#555555')]),
        sheet_zone(4, 0, 12000, 26000, 12000, 'KPI Average'),
        sheet_zone(5, 26000, 12000, 26000, 12000, 'KPI Count'),
        sheet_zone(6, 52000, 12000, 26000, 12000, 'KPI Pass'),
        sheet_zone(7, 0, 24000, 39000, 37000, 'Category Comparison'),
        sheet_zone(8, 39000, 24000, 39000, 37000, 'Score Distribution'),
        sheet_zone(9, 0, 61000, 78000, 39000, 'Scores by Category'),
        text_zone(10, 78000, 12000, 22000, 4000, [text_run('Filters', bold='true', fontsize='12')]),
        filter_zone(11, 78000, 16000, 22000, 7000, 'Score Distribution', r('none:model_version:nk'), 'checkdropdown'),
        filter_zone(12, 78000, 23000, 22000, 7000, 'Score Distribution', r('none:category_label:nk'), 'checkdropdown'),
        filter_zone(13, 78000, 30000, 22000, 7000, 'Score Distribution', r('none:date:qk'), 'slider'),
        legend_zone(15, 78000, 37000, 22000, 9000, 'Category Comparison', r('usr:Calculation_status:nk')),
        text_zone(14, 78000, 46000, 22000, 54000, [
            text_run('What this means\n\n', bold='true', fontsize='12', fontcolor='#1f3b57'),
            text_run('Reasoning is the weak spot: average about 41, and 7 in 10 answers score below 50.\n\n'
                     'Code and tool calling are middling (about 48-50) and inconsistent.\n\n'
                     'Knowledge and instruction following are strong (66-72).\n\n'
                     'The model barely matters: all four are within about 4 points in every category.\n\n',
                     fontsize='10'),
            text_run('Recommendation: ', bold='true', fontsize='10'),
            text_run('focus improvement work on reasoning and tool calling before switching models.',
                     fontsize='10')]),
    ]
    actions = filter_action(DASH, 'Category Comparison', 'Click a category to filter', 1)
    xml = workbook(ds_xml, ''.join(sheets), dashboard(DASH, zones), actions, windows(DASH, sheet_names))
    package('evaluation_score_dashboard.twb', xml, 'evaluation_data_clean.csv')


# ------------------------------------------------------------------------- judge book

JDS = 'federated.0judgeagreement000000000000'
JCAP = 'Judge agreement'
JDASH = 'Judge Agreement Analysis Dashboard'


def jr(inst):
    return f'[{JDS}].[{inst}]'


def judge_book():
    J_CAT = column('category', 'string', 'dimension', 'nominal', caption='Category')
    J_DATE = column('date', 'date', 'dimension', 'ordinal', caption='Date')
    J_J1 = column('judge_1_score', 'real', 'measure', 'quantitative', caption='Judge 1 score')
    J_J2 = column('judge_2_score', 'real', 'measure', 'quantitative', caption='Judge 2 score')
    J_DIFF = column('score_difference', 'real', 'measure', 'quantitative',
                    caption='Gap between judges (points)', fmt='n#,##0.0')
    J_AGR = column('agreement', 'integer', 'measure', 'quantitative', caption='Agreement rate', fmt='p0%')
    J_ID = column('evaluation_id', 'integer', 'dimension', 'ordinal', caption='Evaluation ID')
    J_N = column('Calculation_n', 'integer', 'measure', 'quantitative', caption='Number of answers',
                 fmt='n#,##0', formula='COUNT([evaluation_id])')
    J_BAND = column('Calculation_gap', 'integer', 'dimension', 'ordinal',
                    caption='Gap between judges (5-point bands)',
                    formula='MIN(INT([score_difference]/5)*5, 50)')
    J_AGREES = column('Calculation_agrees', 'string', 'dimension', 'nominal', caption='Judges agree?',
                      formula='IIF([agreement] = 1, "Agree (within 10 points)", "Disagree")')

    i_cat = ('category', 'None', 'none:category:nk', 'nominal')
    i_date = ('date', 'None', 'none:date:qk', 'quantitative')
    i_agr = ('agreement', 'Avg', 'avg:agreement:qk', 'quantitative')
    i_diff = ('score_difference', 'Avg', 'avg:score_difference:qk', 'quantitative')
    i_cnt = ('Calculation_n', 'User', 'usr:Calculation_n:qk', 'quantitative')
    i_band = ('Calculation_gap', 'None', 'none:Calculation_gap:ok', 'ordinal')
    i_j1 = ('judge_1_score', 'None', 'none:judge_1_score:qk', 'quantitative')
    i_j2 = ('judge_2_score', 'None', 'none:judge_2_score:qk', 'quantitative')
    i_agrees = ('Calculation_agrees', 'None', 'none:Calculation_agrees:nk', 'nominal')

    fcols, finst = [J_CAT, J_DATE], [i_cat, i_date]
    filters = cat_filter(JDS, 'none:category:nk', 2) + date_filter(JDS, 'none:date:qk', 3)
    ds_xml = datasource(JDS, JCAP, 'judge_agreement_data.csv',
                        [('evaluation_id', 'integer'), ('category', 'string'),
                         ('judge_1_score', 'real'), ('judge_2_score', 'real'),
                         ('score_difference', 'real'), ('agreement', 'integer'), ('date', 'date')],
                        [J_CAT, J_DATE, J_J1, J_J2, J_DIFF, J_AGR, J_ID, J_N, J_BAND, J_AGREES],
                        palettes=[(i_agrees, {'Agree (within 10 points)': '#2e7d32', 'Disagree': '#c62828'})])
    sheets = []
    for name, inst, cap, cols in [
        ('KPI Agreement', i_agr, 'Judges agree (within 10 points)', [J_AGR]),
        ('KPI Gap', i_diff, 'Average gap between judges (points)', [J_DIFF]),
        ('KPI Evaluations', i_cnt, 'Answers scored by both judges', [J_N, J_ID]),
    ]:
        sheets.append(kpi_sheet(name, JDS, JCAP, deps(JDS, cols + fcols, [inst] + finst),
                                inst[2], cap, filters))
    sheets.append(worksheet(
        'Agreement by Category', JDS, JCAP,
        deps(JDS, [J_CAT, J_AGR, J_DATE], [i_cat, i_agr, i_date]),
        rows=jr('none:category:nk'), cols=jr('avg:agreement:qk'), mark='Bar',
        encodings=f'<color column="{jr("avg:agreement:qk")}" />', filters=filters,
        sorts=f'<sort class="computed" column="{jr("none:category:nk")}" direction="DESC" '
              f'using="{jr("avg:agreement:qk")}" />',
        pane_style=labels_on(), title='How often do the two judges agree, by task type?'))
    sheets.append(worksheet(
        'Disagreement Distribution', JDS, JCAP,
        deps(JDS, [J_BAND, J_ID, J_N, J_AGREES] + fcols, [i_band, i_cnt, i_agrees] + finst),
        rows=jr('usr:Calculation_n:qk'), cols=jr('none:Calculation_gap:ok'), mark='Bar',
        encodings=f'<color column="{jr("none:Calculation_agrees:nk")}" />', filters=filters,
        title='How far apart are the judges? (answers per 5-point gap; 0 = same score)'))
    sheets.append(worksheet(
        'Judge Comparison', JDS, JCAP,
        deps(JDS, [J_J1, J_J2, J_CAT, J_AGREES, J_DATE], [i_j1, i_j2, i_cat, i_agrees, i_date]),
        rows=jr('none:judge_2_score:qk'), cols=jr('none:judge_1_score:qk'), mark='Circle',
        encodings=f'<color column="{jr("none:Calculation_agrees:nk")}" />', filters=filters,
        aggregated=False,
        pane_style='<style-rule element="mark"><format attr="mark-transparency" value="60" /><format attr="size" value="0.3" /></style-rule>',
        title='Judge 1 vs judge 2 on the same answer (dots near the trend line = judges agree)',
        pane_extra='<trendline enable-confidence-bands="false" enable-instant-analytics="true" '
                    'enabled="true" exclude-color="true" exclude-intercept="false" fit="linear" />'))

    names = ['KPI Agreement', 'KPI Gap', 'KPI Evaluations', 'Agreement by Category',
             'Disagreement Distribution', 'Judge Comparison']
    zones = [
        text_zone(3, 0, 0, 100000, 12000, [
            text_run('Judge Agreement Analysis Dashboard\n', bold='true', fontsize='20', fontcolor='#1f3b57'),
            text_run('How often do two independent judges give the same answer a similar score? '
                     'Higher agreement means the scores on the main dashboard can be trusted. '
                     'Agreement = the two scores are within 10 points of each other (0-100 scale).',
                     fontsize='11', fontcolor='#555555')]),
        sheet_zone(4, 0, 12000, 26000, 12000, 'KPI Agreement'),
        sheet_zone(5, 26000, 12000, 26000, 12000, 'KPI Gap'),
        sheet_zone(6, 52000, 12000, 26000, 12000, 'KPI Evaluations'),
        sheet_zone(7, 0, 24000, 39000, 38000, 'Agreement by Category'),
        sheet_zone(8, 39000, 24000, 39000, 38000, 'Disagreement Distribution'),
        sheet_zone(9, 0, 62000, 78000, 38000, 'Judge Comparison'),
        text_zone(10, 78000, 12000, 22000, 4000, [text_run('Filters', bold='true', fontsize='12')]),
        filter_zone(11, 78000, 16000, 22000, 7000, 'Agreement by Category', jr('none:category:nk'), 'checkdropdown'),
        filter_zone(12, 78000, 23000, 22000, 7000, 'Agreement by Category', jr('none:date:qk'), 'slider'),
        legend_zone(14, 78000, 30000, 22000, 7000, 'Disagreement Distribution', jr('none:Calculation_agrees:nk')),
        text_zone(13, 78000, 37000, 22000, 63000, [
            text_run('What this means\n\n', bold='true', fontsize='12', fontcolor='#1f3b57'),
            text_run('The judges agree only about 56% of the time, and the rate is similar in every task type '
                     '(53-59%).\n\nRoughly 1 in 8 answers gets scores more than 20 points apart, which is '
                     'enough to move an answer from "acceptable" to "needs improvement".\n\n', fontsize='10'),
            text_run('Recommendation: ', bold='true', fontsize='10'),
            text_run('tighten the scoring guide, and add a third judge for answers where the first two '
                     'disagree, before using small score differences to make decisions.', fontsize='10')]),
    ]
    actions = filter_action(JDASH, 'Agreement by Category', 'Click a category to filter', 1)
    xml = workbook(ds_xml, ''.join(sheets), dashboard(JDASH, zones), actions, windows(JDASH, names))
    package('judge_agreement_dashboard.twb', xml, 'judge_agreement_data.csv')


if __name__ == '__main__':
    eval_book()
    judge_book()
