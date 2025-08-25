example1 = '''
[Reasoning]
Q1: How many subgoals are contained in the task "fly to wind turbine nearby and inspect whether it works"?
A1: There are two subgoals in the given task. One is to fly to the wind turbine, and the other is to inspect whether it works.
Q2: In subgoal 1, what are the subtasks needed to complete it?
A2: There are four subtasks in subgoal 1: takeoff, look for wind turbines, move vehicle to a place nearby wind turbine, and inspect with question "Does the wind turbine in current view work well?".
Q3: For the action "look for", what object needs to be found?
A3: For the action "look for", the object that needs to be found is "wind turbine".
Q4: For the action "move_to", what is the destination?
A4: For the action "move_to", the destination is "a place nearby wind turbine".
Q5: For the action "inspect", what is the specific question to be answered?
A5: For the action "inspect", the specific question to be answered is "Does the wind turbine in current view work well?".
Q6: What is the most appropriate first action to begin the mission?
A6: The most appropriate first action is "takeoff" to launch the drone.

[Plan]
{
  "mission": "fly to wind turbine nearby and inspect whether it works",
  "current_step": {
    "description": "Take off the drone",
    "action": {
      "type": "takeoff",
      "vehicle": "Drone1"
    }
  },
  "to_do_list": [
    "Look for wind turbines",
    "Move vehicle to a place nearby wind turbine",
    "Inspect with question 'Does the wind turbine in current view work well?'"
  ]
}
'''

example2 = '''
[Reasoning]
Q1: How many subgoals are contained in the task "inspect the nearby wind turbine"?
A1: There are two subgoals in the given task. One is to locate and approach the nearby wind turbine, and the other is to inspect the wind turbine.
Q2: In subgoal 1, what are the subtasks needed to complete it?
A2: There are three subtasks in subgoal 1: takeoff, look for wind turbines, and move vehicle to a place nearby wind turbine.
Q3: For the action "look for", what object needs to be found?
A3: For the action "look for", the object that needs to be found is "wind turbine".
Q4: For the action "move_to", what is the destination?
A4: For the action "move_to", the destination is "a place nearby wind turbine".
Q5: In subgoal 2, what are the subtasks needed to complete the inspection?
A5: There are two subtasks in subgoal 2: inspect with question "Does the wind turbine in current view work well?" and inspect with question "Are there any visible damages on the wind turbine?".
Q6: For the first "inspect" action, what is the specific question to be answered?
A6: For the first "inspect" action, the specific question to be answered is "Does the wind turbine in current view work well?".
Q7: For the second "inspect" action, what is the specific question to be answered?
A7: For the second "inspect" action, the specific question to be answered is "Are there any visible damages on the wind turbine?".
Q8: What is the most appropriate first action to begin the mission?
A8: The most appropriate first action is "takeoff" to launch the drone.

[Plan]
{
  "mission": "inspect the nearby wind turbine",
  "current_step": {
    "description": "Take off the drone",
    "action": {
      "type": "takeoff",
      "vehicle": "Drone1"
    }
  },
  "to_do_list": [
    "Look for wind turbines",
    "Move vehicle to a place nearby wind turbine",
    "Inspect with question 'Does the wind turbine in current view work well?'",
    "Inspect with question 'Are there any visible damages on the wind turbine?'"
  ]
}
'''