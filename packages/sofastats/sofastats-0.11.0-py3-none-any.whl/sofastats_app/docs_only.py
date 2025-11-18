

# from pathlib import Path
# from sofastats.output.stats.anova import AnovaDesign
#
#
# stats = AnovaDesign(
#     grouping_field_name='star_preference',
#     group_values=['Start Trek', 'Star Wars', 'Neither'],
#     measure_field_name='iq',
#     csv_file_path=Path('science_fiction.csv'),
# )
# ## print raw results to console
# print(stats.to_result())
# ## save full HTML results to a file
# html_design = stats.to_html_design()
# html_design.to_file(
#     fpath=Path('anova_demo.html'), html_title='ANOVA')
#
# stats = AnovaDesign(
#     grouping_field_name='country',
#     group_values=[1, 2, 3],
#     data_labels_yaml_file_path=Path('data_labels.yaml'),
#     measure_field_name='height',
#     csv_file_path=Path('sports.csv'),
# )
# etc ...