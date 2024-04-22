

import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.camera import Camera
from viam.services.vision import VisionClient
from speech_service_api import SpeechService
import google.generativeai as genai
import speech_recognition as sr


async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key='YOUR_API_KEY',
      api_key_id='YOUR_API_KEY_ID'
    )
    return await RobotClient.at_address('samraspi4-main.7gp2t3f5ie.viam.cloud', opts)

async def recognize_speech():
    mic = sr.Microphone(device_index = 0)
    r = sr.Recognizer()
    text = ''
    with mic as source:
        print('Say Sommething')
        audio = r.listen(source)
        print("Audio: ", audio)
        text = r.recognize_whisper_api(audio, api_key="YOUR_API_KEY")
    return text

async def main():
    robot = await connect()

    # make sure that your detector name in the app matches "myPeopleDetector"
    myPeopleDetector = VisionClient.from_robot(robot, "myPeopleDetector")
    # make sure that your camera name in the app matches "my-camera"
    my_camera = Camera.from_robot(robot, name="cam")
    
    #For Speechio
    speech = SpeechService.from_robot(robot, name="speech")
    

    api_key = "YOUR_API_KEY"
    #print(api_key)
    genai.configure(api_key=api_key)

    #Chat model
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    chat = model.start_chat()
    #Vision model
    visionModel = genai.GenerativeModel('gemini-pro-vision')

    #prompt instruction
    answer_criteria = "Answer the question in no more than two lines."
    
    #Person Detection loop
    while (True):
        print("Looking for People...")
        img = await my_camera.get_image(mime_type="image/jpeg")
        detections = await myPeopleDetector.get_detections(img)

        #detecting person based on curstom threshold value
        found = False
        for d in detections:
            if d.confidence > 0.5 and d.class_name.lower() == "person":
                print("This is a person!")
                found = True
        
        #the interaction mode starts from here if the system founds someone
        while (found):
            await speech.say('Hello There, How May I helpyou today?', True)
            print('Ready To Listen to know...........')
            #Get User Response
            user_input = await recognize_speech()
            print('Recognized Speech: ', user_input)

            #Chat loop
            if 'tell me' in user_input.lower():
                #constructing the prompt for chat model
                prompt = answer_criteria + "question: " + user_input
                print("Prompt: ", prompt)
                response = chat.send_message(prompt)
                print(response.text) 
                
                #get output via speaker upon getting reponse back from Gemini
                if len(response.text) > 0:
                    await speech.say(response.text, True) 
                
                #Follow-Up loop
                while (True):
                    await speech.say("Is there anything else I can help you with?", True)
                    print("Ready to Listen...")
                    follow_up_input = await recognize_speech()
                    print('follow_up_input: ', follow_up_input)
                    if "yes" in follow_up_input.lower():
                        follow_up_prompt = answer_criteria + "question: " + follow_up_input
                        print("Follow_up Prompt: ", follow_up_prompt)
                        response = chat.send_message(follow_up_prompt)
                        if len(response.text) > 0:
                            await speech.say(response.text, True) #continues the follow-up loop
                    elif "no" in follow_up_input.lower():
                        await speech.say("Cool. Will go back to our main Menu.", True)
                        break #breaks the follow-up loop
                    else:
                        await speech.say("Sorry, I didn't understand. Going back to main menu", True)
                        break #breaks the follow-up loop

            #vision loop  
            elif 'picture' in user_input.lower():
                cam_return_value = await my_camera.get_image()
                print(f"cam get_image return value: {cam_return_value}")
                response = visionModel.generate_content([cam_return_value, "Explain what is this image?"])
                print(response.text)
                if len(response.text) > 0:
                    await speech.say(response.text, True)
                
                #Follow-Up loop
                while (True):
                    await speech.say("Is there anything else I can help you with?", True)
                    print("Ready to Listen...")
                    follow_up_input = await recognize_speech()
                    print('follow_up_input: ', follow_up_input)
                    if "yes" in follow_up_input.lower():
                        #Chat model for Image questions
                        model = genai.GenerativeModel('gemini-1.0-pro-latest')
                        # chat model instance for follow-up questions for the taken image 
                        chatImageInstance = model.start_chat()

                        #adds the previous response to the prompt to facilitates follow-up questions for the given image input
                        image_answer_criteria = "previous response: " + response.text+ "Use the context to answer the question. If answer can not found from the context you can use your knowledge to answer the question." + answer_criteria
                        follow_up_prompt = image_answer_criteria + "question: " + follow_up_input
                        print("Follow_up Prompt: ", follow_up_prompt)
                        response = chatImageInstance.send_message(follow_up_prompt)
                        if len(response.text) > 0:
                            await speech.say(response.text, True) #continues the follow-up loop
                    elif "no" in follow_up_input.lower():
                        await speech.say("Cool. Will go back to our main Menu.", True)
                        break #breaks the follow-up loop
                    else:
                        await speech.say("Sorry, I didn't understand. Going back to main menu", True)
                        break #breaks the follow-up loop

            #end of interaction                
            else:
                await speech.say("Cool. Hope you have a great rest of the day", True)
                break	
	 
                

                
    # Don't forget to close the machine when you're done!
    await robot.close()


if __name__ == '__main__':
    asyncio.run(main())

