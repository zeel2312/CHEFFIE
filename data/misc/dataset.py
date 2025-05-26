import kaggle

kaggle.api.authenticate()

kaggle.api.dataset_download_files('hugodarwood/epirecipes', path = '.', unzip = True)