# Merval_Analysis_Tool
This is a web app that allow us to analyze different aspects of the Merval Stock Market

# Reproducing this web app 
To recreate this web app on your own computer, do the following.
(explanation from https://github.com/dataprofessor)

### Create conda environment
Firstly, we will create a conda environment called *stock*
```
conda create -n stock python=3.7.9
```
Secondly, we will login to the *stock* environement
```
conda activate stock
```
### Install prerequisite libraries

Download requirements.txt file

```
wget https://github.com/Chaspeer/Merval_Analysis_Tool/requirements.txt

```

Pip install libraries
```
pip install -r requirements.txt
```

###  Download and unzip contents from GitHub repo

Download and unzip contents from https://github.com/Chaspeer/Merval_Analysis_Tool

###  Launch the app

```
streamlit run merval.py
```
