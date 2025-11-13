# i050-utility-package

##  Brief Description
The **`i050-utility-package`** is a dedicated data cleaning utility built for users working with the `pandas` library. Its primary goal is to streamline the data preparation phase of any project by automating common sanitization tasks.

##  What It Does (Core Functionality)
The core function, `sanitize_dataframe`, performs the following automated cleaning operations on a Pandas DataFrame:
1.  **Standardizes Strings:** Converts all string entries (object/text type columns) to lowercase and removes leading/trailing whitespace.
2.  **Handles Missing Data:** Automatically drops any rows containing `None` or `NaN` values.

##  Installation
You can install the package directly from PyPI using `pip`.

```bash
pip install i050-utility-package
