import datasets
import os

class RandomStreetViewConfig(datasets.BuilderConfig):
    """
    BuilderConfig for RandomStreetView
    """

    def __init__(self, data_path, **kwargs):
        super(RandomStreetViewConfig, self).__init__(version=datasets.Version("1.0.0"), **kwargs)
        self.data_path = data_path
        

class RandomStreetViewDatasetHF(datasets.GeneratorBasedBuilder):
    """
    dataset of random street view images
    """

    VERSION = datasets.Version("1.0.0")
    BUILDER_CONFIGS = [
        datasets.BuilderConfig(
            name="panoramic",
            version=VERSION,
            description="3 angles combined into one image for a single location",
        ),
        datasets.BuilderConfig(
            name="raw",
            version=VERSION,
            description="3 images at different angle per one location, used to build panoramic",
        ),
    ]


    DEFAULT_CONFIG_NAME = "panoramic"

    def _info(self):
        # TODO: This method specifies the datasets.DatasetInfo object which contains informations and typings for the dataset
        if self.config.name == "panoramic":  # This is the name of the configuration selected in BUILDER_CONFIGS above
            features = datasets.Features(
                {
                    "image": datasets.Image(),
                    "label": datasets.ClassLabel(names = _NAMES)
                    # These are the features of your dataset like images, labels ...
                }
            )
        else:  #if self.config.name == "raw":  # This is an example to show how to have different features for "first_domain" and "second_domain"
            features = datasets.Features(
                {  
                    "image": datasets.Image(),
                    "label": datasets.ClassLabel(names = _NAMES)
                }
            )
        return datasets.DatasetInfo(
            # This is the description that will appear on the datasets page.
            description= """
                The random streetview images dataset are panoramic images scraped from randomstreetview.com,
                which shows a random location accessible by Google Streetview. The dataset was designed with 
                the intent to geolocate an image purely based on its visual content.
            """,
            # This defines the different columns of the dataset and their types
            features=features,  # Here we define them above because they are different between the two configurations
            
            # If there's a common (input, target) tuple from the features, uncomment supervised_keys line below and
            # specify them. They'll be used if as_supervised=True in builder.as_dataset.
            supervised_keys=("image", "label"),
            
            # Homepage of the dataset for documentation
            homepage=_HOMEPAGE,
            # License for the dataset if available
            license=_LICENSE,
            # Citation for the dataset
            citation=_CITATION,
            task_templates=[ImageClassification(image_column="image", label_column="label")]
        )

    def _split_generators(self, dl_manager):
            # TODO: This method is tasked with downloading/extracting the data and defining the splits depending on the configuration
            # If several configurations are possible (listed in BUILDER_CONFIGS), the configuration selected by the user is in self.config.name

            # dl_manager is a datasets.download.DownloadManager that can be used to download and extract URLS
            # It can accept any type or nested list/dict and will give back the same structure with the url replaced with path to local files.
            # By default the archives will be extracted and a path to a cached folder where they are extracted is returned instead of the archive
            
            #urls = _URLS[self.config.name]
            #dl_manager.download_and_extract(urls)
            data_dir = '../data/rsv' 
            return [
                datasets.SplitGenerator(
                    name=datasets.Split.TRAIN,
                    # These kwargs will be passed to _generate_examples
                    gen_kwargs={
                        "images": dl_manager.iter_archive(data_dir),
                        #"filepath": os.path.join(data_dir, "panoramic/"),
                        "split": "train",
                    },
                ),

                # TODO: Not ready yet
                # datasets.SplitGenerator(
                #     name=datasets.Split.VALIDATION,
                #     # These kwargs will be passed to _generate_examples
                #     gen_kwargs={
                #         "filepath": os.path.join(data_dir, "dev.jsonl"),
                #         "split": "dev",
                #     },
                # ),
                # datasets.SplitGenerator(
                #     name=datasets.Split.TEST,
                #     # These kwargs will be passed to _generate_examples
                #     gen_kwargs={
                #         "filepath": os.path.join(data_dir, "test.jsonl"),
                #         "split": "test"
                #     },
                # ),
            ]

    # method parameters are unpacked from `gen_kwargs` as given in `_split_generators`
    def _generate_examples(self, filepath):
        # TODO: This method handles input defined in _split_generators to yield (key, example) tuples from the dataset.
        # The `key` is for legacy reasons (tfds) and is not important in itself, but must be unique for each example.
        
        with open(filepath, encoding="utf-8") as f:
            for key, row in enumerate(f):
                data = json.loads(row)

                if self.config.name == "panoramic":
                    # Yields examples as (key, example) tuples
                    yield key, {
                        "image": data["image"],
                        "label": data["label"],
                    }
                
                else: # self.config.name == "raw":
                    yield key, {
                        "image": data["image"],
                        "label": data["label"],
                    }