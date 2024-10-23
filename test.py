    def AI_pick_target_to_go(self, character):
        # choosing enemy from self list, random choice, cannot be attacked
        targets = []
        
        if character.team == 1:
            for target in self.character_manager.instance_event_manager.team_two:
                targets.append(target)
        if character.team == 2:
            for target in self.character_manager.instance_event_manager.team_one:
                targets.append(target)
        
        # choose closes target
        val = float('inf')
        for target in targets:
            path = self.character_manager.instance_algorithms.calc_pts_alongtheway (character.position, target.position)
            if len(path)<val:
                best_target = target
                
                
                
                
                        # # Split input into action and target (if target exists)
        # parts = action_input.split(maxsplit=1)
        # command = parts[0]
        # target = (parts[1] if len(parts) > 1 else None).title()  # target is the second word, if present
        
        # # Normalize the list items by converting them to lowercase and replacing spaces with underscores
        # actions_mapping = {action.lower().replace(" ", "_"): action for action in actions_list}
        
        # # Search for a partial match in the input command
        # for normalized_action, original_action in actions_mapping.items():
        #     if command in normalized_action:
        #         if "attack" in normalized_action and target:
        #             #check for valid enemy
        #             return target
                
        #         # if not attack
        #         action_method = getattr(self, normalized_action, None)
        #         if action_method:
        #             action_method(character)
        #         else:
        #             print(f"Action '{original_action}' is not yet implemented.")
        #         return  # Exit after the first match

        # print("Action not recognized. Please try again.")
        
        
        
        
        
                
        # #check if char can attack from distance
        # target = self.character_manager.instance_action.choose_ranged_target (character)
        # if target:
        #     self.character_manager.instance_action.main_attack (character, target)
        #     action = False
    
        # #check if targets can be attacked by AI
        # targets = self.character_manager.instance_action.get_targets(character)
        
        # #check if targets can be attacked
        # if not targets:
        #     print(f"DEBUG: AI moving!")
        #     self.move_AI(character)

        # if targets:
        #     target = self.AI_choose_enemy(targets)
        #     print(f"DEBUG: AI attacking!")
        #     self.character_manager.instance_action.main_attack(character, target)