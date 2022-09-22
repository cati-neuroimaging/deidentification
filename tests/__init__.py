import csv
import tempfile


def create_fake_config(config: list) -> str:
    tmp_config = tempfile.NamedTemporaryFile(delete=False)
    with open(tmp_config.name, 'w') as conf:
        conf_writer = csv.writer(conf, delimiter='\t')
        conf_writer.writerow(['Tag', 'Name', 'Action', 'Private Creator'])
        if isinstance(config[0], list):
            conf_writer.writerows(config)
        else:
            conf_writer.writerow(config)
    return tmp_config.name
