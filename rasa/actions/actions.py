# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import datetime as dt
from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionShowTime(Action):

    def name(self) -> Text:
        return "action_show_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=f"{dt.datetime.now()}")

        return []
    


class ActionPersonInfo(Action):
    def name(self):
        return "action_person_info"

    def run(self, dispatcher, tracker, domain):
        person_name = tracker.get_slot('person')
        message = f"If you're asking about {person_name}, Best mate Ever!!! ;-)"
        dispatcher.utter_message(text=message)
        return []

class ActionListCourses(Action):
    def name(self) -> Text:
        return "action_list_courses"

    # def run(self, dispatcher: CollectingDispatcher,
    #         tracker: Tracker,
    #         domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    #     # Construct SPARQL query
    #     query = """
    #         PREFIX ex: <http://example.org/>
    #         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    #         SELECT ?courseName ?courseNumber
    #         WHERE {
    #           ?course a ex:Course ;
    #                   ex:CourseName ?courseName ;
    #                   ex:CourseNumber ?courseNumber .
    #         }
    #         """
    #     sparql_endpoint = "http://localhost:3030/roboprof/sparql"

    #     response = requests.get(sparql_endpoint, params={'query': query})
    #     # print(response.json())
    #     # response = requests.get(sparql_endpoint, params={'format': 'json', 'query': query})
    #     results = response.json()

    #     response_message = "Courses offered by the university:\n"
    #     for result in results["results"]["bindings"]:
    #         course_name = result['courseName']['value']
    #         course_number = result['courseNumber']['value']
    #         response_message += f"{course_name} - {course_number}\n"

    

    #     # dispatcher.utter_message(ex + response_message)
    #     dispatcher.utter_message(response_message)
    #     return []

    def run(self, dispatcher, tracker, domain):
        query = """
            PREFIX ex: <http://example.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?courseName ?courseNumber
            WHERE {
              ?course a ex:Course ;
                      ex:CourseName ?courseName ;
                      ex:CourseNumber ?courseNumber .
            }
            """

        response = requests.post('http://localhost:3030/roboprof/query', data={'query': query})
        
        results = response.json()

        response_message = "Courses offered by the university:\n"
        for result in results["results"]["bindings"]:
            course_name = result['courseName']['value']
            course_number = result['courseNumber']['value']
            response_message += f"{course_name} : {course_number}\n"

        dispatcher.utter_message(response_message)
        return []


class ListCoursesForTopic(Action):
    def name(self) -> Text:
        return "action_courses_for_topic"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        topic = tracker.get_slot('topic')
        if not topic:
            dispatcher.utter_message(text="Please provide a topic.")
            return []

        query = """
            PREFIX ex: <http://example.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?courseName
            WHERE {
                ?topic ex:TopicName "%s" .
                ?topic ex:topic_in_course ?course .
                ?course ex:CourseName ?courseName .
            }
            """ % topic
        response = requests.post('http://localhost:3030/roboprof/query', data={'query': query})

        if response.status_code == 200:
            courses = response.json().get('results', {}).get('bindings', [])
            if courses:
                for course in courses:
                    course_name = course.get('courseName', {}).get('value', '')
                    dispatcher.utter_message(text=f"Course covering topic '{topic}': {course_name}")
            else:
                dispatcher.utter_message(text=f"No courses found covering topic '{topic}'.")
        else:
            dispatcher.utter_message(text="Failed to fetch courses for the topic. Please try again later.")

        return []
    

class TopicsCoveredInCourse(Action):
    def name(self) -> Text:
        return "action_topics_covered_in_course"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.get_slot('course')
        lecture_number = tracker.get_slot('lecture_number')

        if not course or not lecture_number:
            dispatcher.utter_message(text="Please provide both the course-name and lecture number.")
            return []

        query = """
            PREFIX ex: <http://example.org/>
            SELECT ?topicName
            WHERE {
                ?course ex:CourseName "%s" .
                ?lecture ex:lectureNumber "%s" .
                ?topic ex:topic_in_lecture ?lecture .
                ?topic ex:TopicName ?topicName .
            }
            """ % (course, lecture_number)
        response = requests.post('http://localhost:3030/roboprof/query', data={'query': query})

        if response.status_code == 200:
            topics = response.json().get('results', {}).get('bindings', [])
            if topics:
                topic_names = [topic.get('topicName', {}).get('value', '') for topic in topics]
                dispatcher.utter_message(text=f"Topics covered in course '{course}' at lecture {lecture_number}: {', '.join(topic_names)}")
            else:
                dispatcher.utter_message(text=f"No topics found for course '{course}' at lecture {lecture_number}.")
        else:
            dispatcher.utter_message(text="Failed to fetch topics covered in the course. Please try again later.")

        return []
    

class ActionListCoursesInSubject(Action):
    def name(self) -> Text:
        return "action_list_courses_in_subject"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract slots from user input
        slots = tracker.latest_message.get("entities")
        subject = next((slot.get("value") for slot in slots if slot.get("entity") == "subject"), None)

        # Construct SPARQL query
        query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?courseName ?courseNumber
            WHERE {{
              ?course a ex:Course ;
                      ex:CourseName ?courseName ;
                      ex:CourseNumber ?courseNumber ;
                      ex:Subject "{subject}" .  
              ?university a ex:University ;
                          ex:UniversityName "Concordia University" .  
            }}
            """

        sparql_endpoint = "http://localhost:3030/roboprof/query"

        # Execute SPARQL query
        response = requests.get(sparql_endpoint, params={'query': query})
        results = response.json()

        if results["results"]["bindings"]:
            # Format response message
            response_message = "Courses offered by the university within the subject:\n"
            for result in results["results"]["bindings"]:
                course_name = result['courseName']['value']
                course_number = result['courseNumber']['value']
                response_message += f"{course_name} : {course_number}\n"
        else:
            response_message = f"No courses found for {subject}."

        # Send formatted message as bot response
        dispatcher.utter_message(text=response_message)

        return []
    

class ActionListMaterials(Action):
    def name(self) -> Text:
        return "action_list_materials"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extracting values of topic and course slots
        topic = tracker.get_slot("topic")
        course = tracker.get_slot("course")

        # Constructing SPARQL query
        query = f"""
            PREFIX ex: <http://example.org/>
            SELECT ?content
            WHERE {{
                ?topic ex:TopicName "{topic}" .
                ?topic ex:topic_in_lecture ?lecture .
                ?lecture ex:Content ?content .
            }}
            """

        sparql_endpoint = "http://localhost:3030/roboprof/query"

        # Executing SPARQL query
        response = requests.get(sparql_endpoint, params={'query': query})
        results = response.json()

        # Extracting recommended materials from the query results
        if "results" in results and "bindings" in results["results"]:
            for result in results["results"]["bindings"]:
                if "content" in result:
                    recommended_materials = result["content"]["value"]
                    dispatcher.utter_message(text=f"Recommended materials for {topic} in {course}: {recommended_materials}")
                    return []

        # If no materials found, utter a message indicating so
        dispatcher.utter_message(text=f"No materials found for {topic} in {course}.")
        return []
    
class ActionListCourseCredits(Action):
    def name(self) -> Text:
        return "action_list_course_credits"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract course and number entities from user's message
        number_entity = tracker.get_slot("course_number")
        

        # Construct SPARQL query
        query = f"""
            PREFIX ex: <http://example.org/>
            SELECT ?credits WHERE {{
                ?course ex:CourseNumber "{number_entity}" ;
                        ex:Credits ?credits .
            }}
            """
        sparql_endpoint = "http://localhost:3030/roboprof/query"

        # Execute query
        response = requests.get(sparql_endpoint, params={'query': query})

        try:
            # Parse response as JSON
            results = response.json()
            credits = results["results"]["bindings"][0]["credits"]["value"]
            response_message = f"The course {number_entity} is worth {credits} credits."
            dispatcher.utter_message(text=response_message)
        except (ValueError, KeyError, IndexError):
            dispatcher.utter_message(text="Sorry, I couldn't retrieve the credits for that course.")
        
        return []
    
class ActionListAdditionalResources(Action):
    def name(self) -> Text:
        return "action_list_additional_resources"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get course number from slot
        course_number = tracker.get_slot("course_number")

        # Construct SPARQL query
        query = f"""
            PREFIX ex: <http://example.org/>

            SELECT ?webpageLink
            WHERE {{
              ?course ex:CourseNumber "{course_number}" ;
                      ex:WebpageLink ?webpageLink .
            }}
            """
        sparql_endpoint = "http://localhost:3030/roboprof/query"

        # Execute query
        response = requests.get(sparql_endpoint, params={'query': query})
        results = response.json()

        # Check if results are empty
        if results['results']['bindings']:
            # Extract webpage link
            webpage_link = results['results']['bindings'][0]['webpageLink']['value']
            response_message = f"Additional resources for course {course_number} are available at the following link: {webpage_link}"
        else:
            response_message = f"No additional resources found for course {course_number}"

        # Utter the response
        dispatcher.utter_message(text=response_message)
        return []
    
# Detail the content (slides, worksheets, readings) available for [lecture number] in [course] [number].
class ActionListContentDetails(Action):
    def name(self) -> Text:
        return "action_list_content_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course_number = tracker.get_slot("course_number")
        lecture_number = 3 #tracker.get_slot("lecture_number")

        # Construct SPARQL query
        query = f"""
            PREFIX ex: <http://example.org/>
            SELECT ?content
            WHERE {{
                ?course ex:CourseNumber "{course_number}" .
                ?lecture ex:lectureNumber  "{lecture_number}" .
                ?lecture ex:Content ?content .
            }}
            """
        sparql_endpoint = "http://localhost:3030/roboprof/query"

        # Execute query
        response = requests.get(sparql_endpoint, params={'query': query})
        results = response.json()

        # Format response
        response_message = "Content available for lecture {} in course {}:\n".format(lecture_number, course_number)
        for result in results["results"]["bindings"]:
            content = result['content']['value']
            response_message += f"{content}\n"

        dispatcher.utter_message(text=response_message)
        return []
    
class ActionReadingMaterials(Action):
    def name(self) -> Text:
        return "action_reading_materials"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extracting entities from user's message
        course = tracker.get_slot("course")
        topic = tracker.get_slot("topic")

        if course and topic:
            # Construct SPARQL query
            query = f"""
                PREFIX ex: <http://example.org/>
                SELECT ?content
                WHERE {{
                    ?course ex:CourseName "{course}" .
                    ?topic ex:topic_in_lecture ?lecture .
                    ?lecture ex:Content ?content .
                }}
                """
            sparql_endpoint = "http://localhost:3030/roboprof/query"

            # Execute query
            response = requests.get(sparql_endpoint, params={'query': query})
            results = response.json()

            # Extract reading materials from the response
            reading_materials = []
            for result in results["results"]["bindings"]:
                content = result['content']['value']
                reading_materials.append(content)

            if reading_materials:
                # Construct response message
                response_message = f"Reading materials recommended for studying {topic} in {course}:\n"
                for material in reading_materials:
                    response_message += f"- {material}\n"
                dispatcher.utter_message(text=response_message)
            else:
                dispatcher.utter_message(text="Sorry, no reading materials found for the specified topic and course.")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't understand the topic or course you mentioned.")

        return []

class ActionListCompetencies(Action):
    def name(self) -> Text:
        return "action_list_competencies"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract course number from slot
        course_number = tracker.get_slot("completed_course")

        if course_number is None:
            dispatcher.utter_message(text="I'm sorry, I didn't catch the course number.")
            return []

        # Construct SPARQL query
        query = f"""
            PREFIX ex: <http://example.org/>
            SELECT ?competency
            WHERE {{
              ?student ex:completedCourse "{course_number}" ;
                       ex:competentIn ?competency .
            }}
            """
        sparql_endpoint = "http://localhost:3030/roboprof/query"

        # Execute query
        response = requests.get(sparql_endpoint, params={'query': query})
        results = response.json()

        # Format response into a string message
        response_message = f"Competencies gained after completing {course_number}:\n"
        for result in results["results"]["bindings"]:
            competency = result['competency']['value']
            response_message += f"- {competency}\n"

        # Utter the formatted message
        dispatcher.utter_message(text=response_message)
        return []
    

class ActionListGrades(Action):
    def name(self) -> Text:
        return "action_list_grades"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract entities
        student_entity = tracker.get_slot("student")
        course_entity = tracker.get_slot("completed_course")

        def split_name(full_name):
            # Split the full name into parts based on space
            name_parts = full_name.split()
    
            # Extract the first name and last name
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    
            return first_name, last_name

        first_name, last_name = split_name(student_entity)

        # Construct SPARQL query
        query = f"""
            PREFIX ex: <http://example.org/>
            SELECT ?firstName ?lastName ?grade
            WHERE {{
                ?student ex:firstName ?firstName ;
                         ex:lastName ?lastName ;
                         ex:completedCourse "{course_entity}" ;
                         ex:grade ?grade .
                FILTER(?firstName = "{first_name}")
            }}
            """
        sparql_endpoint = "http://localhost:3030/roboprof/query"

        # Execute query
        response = requests.get(sparql_endpoint, params={'query': query})
        results = response.json()

        # Format response into a string message
        response_message = ""
        for result in results["results"]["bindings"]:
            first_name = result['firstName']['value']
            last_name = result['lastName']['value']
            grade = result['grade']['value']
            response_message += f"{first_name} {last_name} achieved {grade} in {course_entity}\n"

        # Utter the formatted message
        dispatcher.utter_message(text=response_message.strip())
        return []
    
class ActionListStudentsByCompletedCourse(Action):
    def name(self) -> Text:
        return "action_list_students_by_completed_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the value of the completed_course entity
        completed_course = tracker.get_slot("completed_course")

        # Construct SPARQL query
        query = f"""
            PREFIX ex: <http://example.org/>

            SELECT ?firstName ?lastName
            WHERE {{
              ?student ex:firstName ?firstName ;
                       ex:lastName ?lastName ;
                       ex:completedCourse "{completed_course}" . 
            }}
            """
        sparql_endpoint = "http://localhost:3030/roboprof/query"

        # Execute query
        response = requests.get(sparql_endpoint, params={'query': query})
        results = response.json()

        # Format response
        response_message = f"Students who have completed course {completed_course}:\n"
        for result in results["results"]["bindings"]:
            first_name = result['firstName']['value']
            last_name = result['lastName']['value']
            response_message += f"{first_name} {last_name}\n"

        dispatcher.utter_message(response_message)
        return []
    
class ActionListStudentsTranscript(Action):
    def name(self) -> Text:
        return "action_list_students_transcript"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        student_entity = tracker.get_slot("student")

        def split_name(full_name):
            # Split the full name into parts based on space
            name_parts = full_name.split()
    
            # Extract the first name and last name
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    
            return first_name, last_name

        first_name, last_name = split_name(student_entity)

        # Construct SPARQL query
        query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            SELECT ?completedCourse ?grade
            WHERE {{
              ?student rdf:type ex:Student ;
                       ex:firstName "{first_name}" ;
                       ex:completedCourse ?completedCourse ;
                       ex:grade ?grade .
            }}
            """
        sparql_endpoint = "http://localhost:3030/roboprof/query"

        response = requests.get(sparql_endpoint, params={'query': query})

        # Check if response is empty
        if not response.content:
            dispatcher.utter_message(text="No data found for the student's transcript.")
            return []

        try:
            results = response.json()
            # Format response into a string message
            response_message = f"Transcript for student {student_entity}:\n"
            for result in results["results"]["bindings"]:
                course_name = result['completedCourse']['value']
                grade = result['grade']['value']
                response_message += f"Course: {course_name}, Grade: {grade}\n"

            # Utter the formatted message
            dispatcher.utter_message(text=response_message)
        except ValueError:
            dispatcher.utter_message(text="Error: Unable to parse response from SPARQL endpoint.")

        return []
    

class ActionShowDescription(Action):
    def name(self) -> Text:
        return "action_show_description"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.get_slot("course")
        if not course:
            dispatcher.utter_message(template="utter_show_description_error")
            return []

        # Construct SPARQL query
        query = f"""
            PREFIX ex: <http://example.org/>
            SELECT ?description WHERE {{
                ?course ex:CourseName "{course}" ;
                        ex:Description ?description .
            }}
            """
        sparql_endpoint = "http://localhost:3030/roboprof/query"

        # Execute query
        response = requests.get(sparql_endpoint, params={'query': query})
        results = response.json()

        # Extract description from results
        description = ""
        if "results" in results and "bindings" in results["results"] and results["results"]["bindings"]:
            description = results["results"]["bindings"][0]["description"]["value"]

        # Utter response
        dispatcher.utter_message(text=f"The course {course} is about: {description}")
        return []
    

class ActionListTopicByCourseEvent(Action):
    def name(self) -> Text:
        return "action_list_topic_by_course_event"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get course code from slot
        course_code = tracker.get_slot("course")
        
        #Function to format course code by replacing space with underscore.
        def format_course_code(course_code: str) -> str:
            if " " in course_code:
                return course_code.replace(" ", "_")
            else:
                return course_code

        formatted_course_code = format_course_code(course_code)

        # Construct SPARQL query
        query = f"""
            PREFIX ex: <http://example.org/>

            SELECT DISTINCT ?dbpediaLink ?topicName ?provenance ?topicInLecture
            WHERE {{
              ?topic ex:topic_in_course ex:{formatted_course_code} ;
                     ex:dbpediaLink ?dbpediaLink ;
                     ex:TopicName ?topicName ;
                     ex:provenance ?provenance ;
                     ex:topic_in_lecture ?topicInLecture .
            }}
            """

        sparql_endpoint = "http://localhost:3030/roboprof/query"

        # Execute query
        response = requests.get(sparql_endpoint, params={'query': query})
        results = response.json()

        # Format response into a string message
        response_message = ""
        for result in results["results"]["bindings"]:
            topic_name = result['topicName']['value']
            dbpedia_link = result['dbpediaLink']['value']
            provenance = result['provenance']['value']
            topic_in_lecture = result['topicInLecture']['value']
            response_message += f"Topic: {topic_name}\nDBpedia Link: {dbpedia_link}\nProvenance: {provenance}\nLecture Topic URI: {topic_in_lecture}\n\n"

        # Utter the formatted message
        dispatcher.utter_message(text=response_message)
        return []