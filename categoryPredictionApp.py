# Import required modules
import streamlit as st
import pandas as pd
from rapidfuzz import fuzz, process
from concurrent.futures import ProcessPoolExecutor


# Read in the data with category labelled
df = pd.read_csv("courseWithCategory.csv")


# Create a function to predict category of course
def predictCategory(categoryToPredictFor):
    """categoryToPredictFor = courses we are trying to predict their category for
    return = a dataframe with input course, predicted category and a confidence matching score."""
    
    # Returns best matching course, similarity score and index of the course
    matchedCourse = process.extractOne(categoryToPredictFor, df.courseTitle.values)
    
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
    uploaded_file = st.file_uploader("Upload a file", type=["csv"])
    
    # If any file is uploaded(csv or xlsx)
    if uploaded_file:
        
        # Execute if csv file is uploaded
        try:
            courseToPredict = pd.read_csv(uploaded_file).iloc[:, 0].drop_duplicates().str.lower().str.strip()
            
        # Execute if xlsx file is uploaded
        except:
            st.write("File error!")
        
        # Out a text
        st.subheader("Makeing prediction. Please wait:")
        
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
            matchedDf.to_excel("predictedCategory.xlsx", index=None)
            st.write("File downloaded")
