# Import required modules
import streamlit as st
import pandas as pd
from rapidfuzz import fuzz, process
from concurrent.futures import ProcessPoolExecutor
import base64


# Set a title
st.header("Course Category Prediction App")


# Read in the data with category labelled
df = pd.read_csv("courseWithCategory.csv")


# Create a function to predict category of course
def predictCategory(categoryToPredictFor):
    """categoryToPredictFor = courses we are trying to predict their category for
    return = a dataframe with input course, predicted category and a confidence matching score."""
    
    # Returns best matching course, similarity score and index of the course
    matchedCourse = process.extractOne(categoryToPredictFor, df.courseTitle.values, scorer=fuzz.token_set_ratio)
    
    # Make query by index to extract the broad category
    matchedCategory = df.iloc[matchedCourse[2]].broadCategory1
    
    # Extract similarity score for corresponding category
    matchConfidence = matchedCourse[1]
    
    # Create a dataframe off input course, its corresponding category and similarity score
    matchedDf = pd.DataFrame({
        "categoryFor":categoryToPredictFor,
        "category":matchedCategory,
        "matchConfidence":round(matchConfidence)
    }, index=[0])

    return matchedDf



# This function is executed if more than one course category to predict from uploaded file.
# Use multiprocessing to speed up the computation
def main(categoryToPredictFor):
    with ProcessPoolExecutor() as ex:
        return pd.concat(list(ex.map(predictCategory, categoryToPredictFor))).reset_index(drop=True)


# Create a streamlit checkbox
option = st.radio("Please select an option:",
                 ("Check for a single course", "Check for multiple courses"))

# If user clicks on "Check for a single course" checkbox
if option=="Check for a single course":
    singleCourse = st.text_input("Type in a course name")
    
    # Is a course name is typed in
    if singleCourse:
        st.write(predictCategory(singleCourse))

# If user uploads a file
elif option=="Check for multiple courses":
    st.subheader("Please upload a csv file")
    uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx"])
    
    # If any file is uploaded(csv or xlsx)
    if uploaded_file:
        
        # Execute if csv file is uploaded
        try:
            courseToPredict = pd.read_csv(uploaded_file).iloc[:, 0].drop_duplicates().str.lower().str.strip()
            
        # Execute if xlsx file is uploaded
        except:
            courseToPredict = pd.read_excel(uploaded_file).iloc[:, 0].drop_duplicates().str.lower().str.strip()
        
        # Out a text
        st.subheader("Making prediction. Please wait..")
        
        # Call the main function to predict from
        matchedDf = main(courseToPredict)
        
        # Output the df
        st.write(matchedDf)
        
        
        # Create a checkbox to download the file if clicked
        download = st.radio("Download the prediction data?",
                           ("No", "Yes"))
        if download=="No":
            pass
        
        elif download=="Yes":

            # Create csv download link
            def createDownloadLink(data):
                csv = data.to_csv(index=None).encode()

                b64 = base64.b64encode(csv).decode()

                href = f'<a href="data:file/csv;base64,{b64}" download="categoryPrediction.csv">Download csv file</a>'
                return href

            # Apply the function and return the download link
            st.markdown(createDownloadLink(matchedDf), unsafe_allow_html=True)

# Print my name
st.markdown("<h6 style='text-align: right; color: ash;'>Created by: Faysal</h6>", unsafe_allow_html=True)
