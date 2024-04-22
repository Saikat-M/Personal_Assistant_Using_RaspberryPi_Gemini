# Personal_Assistant_Using_RaspberryPi_Gemini
Personal Assistant using Raspberry Pi, Viam SDK and Gemini API

# The Code Explanation is as follows:
1. Setup and Connection:

    A. Connect function establishes a connection with the robot using the provided API key and ID.

    B. `recognize_speech` function uses `speech_recognition` to capture user speech through the microphone and attempts to recognize it using `recognize_whisper_api`.

3. Main Loop:

    A. Here It connects to the robot and retrieves references to the camera(`cam`), vision detector (`myPeopleDetector`), and the speech service (`speech`) from Viam.

    B. It configures the Google GenerativeAI library with the provided API key.

    C. It creates two instances of generative models:
        chat: `gemini-1.0-pro-latest` model for text chat.
        visionModel: `gemini-pro-vision` model for image analysis.

    D. From here the execution enters into a infinite loop of person detection.

5. Person Detection:

    A. Here it continues look for people until it founds someone to enter into the interaction stage.

    B. It captures an image from the camera.

    C. It uses `myPeopleDetecto`r to analyze the image for people.

    D. If a person is detected with confidence above `50%`

7. After the robot detects a person that satisfy the condition for the above mentioned confidance score, It enters into the Interaction mode.
8. It greets the user.
9. It listens for user input using `recognize_speech` function.
    
    A. `Normal Chat Mode`: If it recognizes `tell me` in user input:
   
        1. Constructs a prompt for the chat model with the user's question and answer criteria.
        2. Sends the prompt to the chat model and receives a response.
        3. Speaks the response back to the user.
        4. It enters a follow-up loop and asks the user if they need further assistance:
            A. If yes, it repeats the chat interaction steps based on the user's follow-up question.
            B. If no, it says goodbye and breaks the follow-up loop.
            C. If the user's response is unclear, it apologizes and restarts the main loop.

    B. `Image Chat Mode`:  If it recognizes `picture` in user input:
   
        1. It captures an image from the camera.
        2. It uses `visionModel` to analyze the image and generate a description.
        3. It speaks the description back to the user.
        4. It enters a follow-up loop similar to the chat interaction but uses a new chat model instance `chatImageInstance` specifically for questions related to the captured  image. This instance utilizes the previous response from the vision model for context and to answer follow-up question rearding the image.

    C.  `End of Interaction`:

        For anything else the system assumes the user doesn't need further assistance in either chat or image analysis interaction loops, the it says goodbye and breaks the main loop.
    
11. Cleanup:

    A. Finally, the main function closes the connection to the robot.
