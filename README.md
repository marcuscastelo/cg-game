# Description

A Game developed only with OpenGL and Python for Computer Graphics course.

# Gameplay video

https://user-images.githubusercontent.com/27441558/183258684-013540a4-664f-4fdf-914c-3f59e8a449b1.mp4

# In-game screenshots

![image](https://user-images.githubusercontent.com/27441558/183258480-0447e048-cf41-4dba-b873-41cb4b9db77a.png)
![image](https://user-images.githubusercontent.com/27441558/183258483-e5aa7663-f94e-4fe2-b294-40f075028c56.png)

# Model screenshots

<details>
  <summary>See images</summary>
  
  ![image](https://user-images.githubusercontent.com/27441558/183258300-c8bf030c-1f3b-4b23-9327-f911c3d78910.png)
  ![image](https://user-images.githubusercontent.com/27441558/183258304-0800f658-4b4d-446e-a2fb-53f65faf6a49.png)
  ![image](https://user-images.githubusercontent.com/27441558/183258309-65f41a96-8e52-461d-87b4-de0ec5db3f53.png)
  ![image](https://user-images.githubusercontent.com/27441558/183258362-ac776847-03c8-46a6-9fce-188b0579a680.png)
  ![image](https://user-images.githubusercontent.com/27441558/183258377-023da458-bf17-4fcc-93e6-83f02e2f2f69.png)
  ![image](https://user-images.githubusercontent.com/27441558/183258389-8e1c6043-8d14-476e-88a3-8597a9633a4d.png)
  ![image](https://user-images.githubusercontent.com/27441558/183258395-eb12a2d3-e43e-4f94-8202-e02c781ad4bd.png)
  ![image](https://user-images.githubusercontent.com/27441558/183258401-a2c39f60-9876-4964-be8b-6eb6ac587174.png)
  ![image](https://user-images.githubusercontent.com/27441558/183258418-0b6a9115-d515-46f8-bf2a-890471b8b656.png)
</details>


# Installation

## Prerequisites

- Python 3.9 or 3.10 (tested with 3.9.6, 3.9.12 and 3.10.10)
- OpenGL 3.3.0 or higher

Clone the repository with `git clone --recursive https://github.com/marcuscastelo/cg-trab`

## Install dependencies

### Linux

`make install-deps`

### Windows (or without make)

`pip install -r requirements.txt`
`cd vendor`
`pip install -e utils`
`pip install -e dpgext`


# Run the game

`make run` 

or

`python src/main.py`

# Controls / Keybinds

- WASD: move the character
- Space: jump
- R: shoot
- E: select object to manipulate in GUI
- Mouse: direction of the character's view
- Ctrl: run (changes FOV and character speed)
- F: inspect weapon 
