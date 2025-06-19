
import sys

from Py4GWCoreLib.Py4GWcorelib import Utils
from Widgets.CustomBehaviors.custom_behavior_base_utility import CustomBehaviorBaseUtility
from Widgets.CustomBehaviors.custom_behavior_party import CustomBehaviorParty
from Widgets.CustomBehaviors.custom_behavior_shared_memory import CustomBehaviorWidgetMemoryManager
from Widgets.CustomBehaviors.custom_skill_utility_base import CustomSkillUtilityBase

# Iterate through all modules in sys.modules (already imported modules)
# Iterate over all imported modules and reload them
for module_name in list(sys.modules.keys()):
    if module_name not in ("sys", "importlib", "cache_data"):
        try:
            if "behavior" in module_name.lower():
                print(f"Reloading module: {module_name}")
                del sys.modules[module_name]
                # importlib.reload(module_name)
                pass
        except Exception as e:
            print(f"Error reloading module {module_name}: {e}")

from typing import List
from HeroAI.cache_data import CacheData
from Py4GWCoreLib import PyImGui, Routines, ActionQueueManager, Player, GLOBAL_CACHE, IconsFontAwesome5, SharedCommandType
from Widgets.CustomBehaviors.custom_behavior_loader import CustomBehaviorLoader, MatchResult
from Widgets.CustomBehaviors.custom_skill import CustomSkill
from Widgets.CustomBehaviors.behavior_state import BehaviorState

party_forced_state_combo = 0
DEBUG = True

def gui():
    PyImGui.set_next_window_size(260, 650)
    # PyImGui.set_next_window_size(460, 800)

    global party_forced_state_combo
    PyImGui.begin("Custom behaviors", )
    shared_data = CustomBehaviorWidgetMemoryManager().GetCustomBehaviorWidgetData("qzd")

    # if DEBUG:
    #     PyImGui.text(f"is_enabled {shared_data.is_enabled}")
    #     PyImGui.text(f"party_target_id {shared_data.party_target_id}")
    #     PyImGui.text(f"party_forced_state {shared_data.party_forced_state}")
    #     PyImGui.text(f"party_forced_state {BehaviorState(shared_data.party_forced_state) if shared_data.party_forced_state is not None else None}")
    #     PyImGui.separator()

    PyImGui.text(f"{IconsFontAwesome5.ICON_USERS} CROSS ACCOUNT ACTIONS")
    if shared_data.is_enabled:
        if PyImGui.button(f"{IconsFontAwesome5.ICON_TIMES} Disable all"):
            CustomBehaviorParty().set_party_is_enable(False)
    else:
        if PyImGui.button(f"{IconsFontAwesome5.ICON_CHECK} Enable all"):
            CustomBehaviorParty().set_party_is_enable(True)

    # PyImGui.same_line(0, 10)

    if shared_data.party_target_id is None:
        if PyImGui.button(f"{IconsFontAwesome5.ICON_CROSSHAIRS} SetPartyCustomTarget"):
            CustomBehaviorParty().set_party_custom_target(GLOBAL_CACHE.Player.GetTargetID())
    else:
        if PyImGui.button(f"{IconsFontAwesome5.ICON_TRASH} ResetPartyCustomTarget"):
            CustomBehaviorParty().set_party_custom_target(None)
        PyImGui.same_line(0, 10)
        PyImGui.text(f"id:{CustomBehaviorParty().get_party_custom_target()}")


    if GLOBAL_CACHE.Map.IsOutpost():
        if PyImGui.button(f"{IconsFontAwesome5.ICON_PLANE} SummonToCurrentMap"):
            account_email = GLOBAL_CACHE.Player.GetAccountEmail()
            self_account = GLOBAL_CACHE.ShMem.GetAccountDataFromEmail(account_email)
            accounts = GLOBAL_CACHE.ShMem.GetAllAccountData()
            for account in accounts:
                if account.AccountEmail == account_email:
                    continue
                print(f"SendMessage {account_email} to {account.AccountEmail}")
                GLOBAL_CACHE.ShMem.SendMessage(account_email, account.AccountEmail, SharedCommandType.TravelToMap, (self_account.MapID, self_account.MapRegion, self_account.MapDistrict, 0))
        # PyImGui.same_line(0, 10)

    if PyImGui.button(f"{IconsFontAwesome5.ICON_ARROW_ALT_CIRCLE_RIGHT} TakeDialogWithTarget"):
        account_email = GLOBAL_CACHE.Player.GetAccountEmail()
        self_account = GLOBAL_CACHE.ShMem.GetAccountDataFromEmail(account_email)
        accounts = GLOBAL_CACHE.ShMem.GetAllAccountData()
        for account in accounts:
            if account.AccountEmail == account_email:
                continue

            print(f"SendMessage {account_email} to {account.AccountEmail}")
            target_id = GLOBAL_CACHE.Player.GetTargetID()
            GLOBAL_CACHE.ShMem.SendMessage(account_email, account.AccountEmail, SharedCommandType.TakeDialogWithTarget, (target_id, ))

        # messaging stuff
        pass

    # items: list[str] = ["None"] + [state.name for state in BehaviorState]
    # party_forced_state_combo = PyImGui.combo("", party_forced_state_combo , items)
    # PyImGui.text(f"State : {items[party_forced_state_combo]} | {CustomBehaviorParty().get_party_forced_state()}")
    # # PyImGui.same_line(0, 10)
    # if PyImGui.button("Apply"):
    #     if items[party_forced_state_combo] == "None":
    #         CustomBehaviorParty().set_party_forced_state(None)
    #     else:
    #         state_string = items[party_forced_state_combo]
    #         state:BehaviorState = BehaviorState[state_string]
    #         CustomBehaviorParty().set_party_forced_state(state)
    PyImGui.text(f"PartyForcedState={CustomBehaviorParty().get_party_forced_state()}")
    if (CustomBehaviorParty().get_party_forced_state() is not None and CustomBehaviorParty().get_party_forced_state().value != BehaviorState.IN_AGGRO.value) or CustomBehaviorParty().get_party_forced_state() is None:
        if PyImGui.button(f"{IconsFontAwesome5.ICON_HAMSA} force to IN_AGGRO"):
            CustomBehaviorParty().set_party_forced_state(BehaviorState.IN_AGGRO)

    if (CustomBehaviorParty().get_party_forced_state() is not None and CustomBehaviorParty().get_party_forced_state().value != BehaviorState.CLOSE_TO_AGGRO.value) or CustomBehaviorParty().get_party_forced_state() is None:
        if PyImGui.button(f"{IconsFontAwesome5.ICON_FEATHER_ALT} force to CLOSE_TO_AGGRO"):
            CustomBehaviorParty().set_party_forced_state(BehaviorState.CLOSE_TO_AGGRO)
            
    if (CustomBehaviorParty().get_party_forced_state() is not None and CustomBehaviorParty().get_party_forced_state().value != BehaviorState.FAR_FROM_AGGRO.value) or CustomBehaviorParty().get_party_forced_state() is None:
        if PyImGui.button(f"{IconsFontAwesome5.ICON_FEATHER_ALT} force to FAR_FROM_AGGRO"):
            CustomBehaviorParty().set_party_forced_state(BehaviorState.FAR_FROM_AGGRO)

    if CustomBehaviorParty().get_party_forced_state() is not None:
        if PyImGui.button(f"{IconsFontAwesome5.ICON_DIZZY} None"):
            CustomBehaviorParty().set_party_forced_state(None)

    PyImGui.separator()

    PyImGui.text(f"{IconsFontAwesome5.ICON_USER_ALT} CURRENT ACCOUNT ACTIONS")
    if DEBUG:
        PyImGui.text(f"PlayerId : {Player.GetAgentID()}")
        # PyImGui.same_line(0, 10)
    PyImGui.text(f"HasLoaded : {CustomBehaviorLoader()._has_loaded}")
    # PyImGui.same_line(0, 10)
    PyImGui.text(f"Selected behavior : {CustomBehaviorLoader().custom_combat_behavior.__class__.__name__}")
    if CustomBehaviorLoader().custom_combat_behavior is not None:
        PyImGui.text(f"Account state:{CustomBehaviorLoader().custom_combat_behavior.get_state()}")
        PyImGui.text(f"Final state:{CustomBehaviorLoader().custom_combat_behavior.get_final_state()}")
    if PyImGui.button(f"{IconsFontAwesome5.ICON_SYNC} Search build again"):
        CustomBehaviorLoader().refresh_custom_behavior_candidate()
    if CustomBehaviorLoader().custom_combat_behavior is not None:
        # PyImGui.same_line(0, 10)

        if CustomBehaviorLoader().custom_combat_behavior.get_is_enabled():
            if PyImGui.button(f"{IconsFontAwesome5.ICON_TIMES} Disable"):
                CustomBehaviorLoader().custom_combat_behavior.disable()
        else:
            if PyImGui.button(f"{IconsFontAwesome5.ICON_CHECK} Enable"):
                CustomBehaviorLoader().custom_combat_behavior.enable()
        pass



    if DEBUG:
        if CustomBehaviorLoader().custom_combat_behavior is not None and type(CustomBehaviorLoader().custom_combat_behavior).mro()[1].__name__ != CustomBehaviorBaseUtility.__name__:
            PyImGui.separator()
            PyImGui.text(f"Generic skills : ")
            generic_behavior_build:List[CustomSkill] = CustomBehaviorLoader().custom_combat_behavior.get_generic_behavior_build()
            if generic_behavior_build is not None:
                for skill in generic_behavior_build:
                    PyImGui.text(f"bbb {skill.skill_name}")

    # print(type(CustomBehaviorLoader().custom_combat_behavior))
    # print(CustomBehaviorBaseUtility)
    # print(type(CustomBehaviorLoader().custom_combat_behavior).mro()[1].__name__)  # Should be CustomBehaviorBaseUtility
    # print(id(CustomBehaviorBaseUtility))
    # print('CustomBehaviorBaseUtility' in type(CustomBehaviorLoader().custom_combat_behavior).mro()[0].__name__)
    # and isinstance(CustomBehaviorLoader().custom_combat_behavior, CustomBehaviorBaseUtility)
    # print(type(CustomBehaviorLoader().custom_combat_behavior).mro()[1].__name__ == CustomBehaviorBaseUtility.__name__)

    if DEBUG:
        if CustomBehaviorLoader().custom_combat_behavior is not None and type(CustomBehaviorLoader().custom_combat_behavior).mro()[1].__name__ == CustomBehaviorBaseUtility.__name__:
            PyImGui.separator()
            PyImGui.text(f"Generic skills - Utility system : ")
            instance: CustomBehaviorBaseUtility = CustomBehaviorLoader().custom_combat_behavior
            # utilities: list[CustomSkillUtilityBase] = instance.get_skills_final_list()

            # for utility in utilities:
            #     PyImGui.text(f"{utility.custom_skill.skill_name} {utility.additive_score_weight}")

            scores: list[tuple[CustomSkillUtilityBase, float | None]] = instance.get_all_scores()

            for score in scores:
                # PyImGui.text(f"{score[0].custom_skill.skill_name} {score[0].additive_score_weight} {score[1]}")
                def label_generic_utility(utility: CustomSkillUtilityBase) -> str:
                    if utility.__class__.__name__ == "GenericUtility":
                        return f"| {IconsFontAwesome5.ICON_GAMEPAD}"
                    return ""

                score_text = f"{score[1]:06.2f}" if score[1] is not None else "ØØØ"
                PyImGui.text(f"{score_text} - {score[0].custom_skill.skill_name} {label_generic_utility(score[0])}")


    if DEBUG:
        PyImGui.separator()
        PyImGui.text(f"All templates : ")
        results: List[MatchResult] | None = CustomBehaviorLoader().get_all_custom_behavior_candidates()
        if results is not None:
            for i, result in enumerate(results):
                PyImGui.text(f"{i}: {result.instance.__class__.__name__} ({result.matching_count} matches /{result.build_size} (total_build_size) => {result.matching_result} score | => {result.is_matched_with_current_build})")
    
    PyImGui.end()

def main():

    if not Routines.Checks.Map.MapValid():
        return

    gui()
    CustomBehaviorLoader().initialize_custom_behavior_candidate()
    if CustomBehaviorLoader().custom_combat_behavior is not None:
        CustomBehaviorLoader().custom_combat_behavior.act(CacheData())

    ActionQueueManager().ProcessQueue("ACTION")

def configure():
    # gui()
    pass

__all__ = ["main", "configure"]
