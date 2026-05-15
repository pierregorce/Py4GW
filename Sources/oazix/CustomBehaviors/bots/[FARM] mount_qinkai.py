from Py4GWCoreLib import Botting, Routines, GLOBAL_CACHE, ModelID, Map, Agent, ConsoleLog, Player
from Sources.oazix.CustomBehaviors.primitives.botting.botting_fsm_helper import BottingFsmHelpers
from Sources.oazix.CustomBehaviors.primitives.botting.botting_helpers import BottingHelpers
from Sources.oazix.CustomBehaviors.primitives.botting.botting_manager import BottingManager
from Sources.oazix.CustomBehaviors.primitives.following_behavior_priority import FollowingBehaviorPriority
from Sources.oazix.CustomBehaviors.primitives.parties.custom_behavior_party import CustomBehaviorParty
from Sources.oazix.CustomBehaviors.primitives.parties.party_following_manager import PartyFollowingManager
from Sources.oazix.CustomBehaviors.skills.botting.move_to_enemy_if_close_enough import MoveToEnemyIfCloseEnoughUtility
from Sources.oazix.CustomBehaviors.skills.botting.move_to_party_member_if_dead import MoveToPartyMemberIfDeadUtility
from Sources.oazix.CustomBehaviors.skills.botting.move_to_party_member_if_in_aggro import MoveToPartyMemberIfInAggroUtility
from Sources.oazix.CustomBehaviors.skills.botting.wait_if_in_aggro import WaitIfInAggroUtility
from Sources.oazix.CustomBehaviors.skills.botting.wait_if_lock_taken import WaitIfLockTakenUtility
from Sources.oazix.CustomBehaviors.skills.botting.wait_if_party_member_mana_too_low import WaitIfPartyMemberManaTooLowUtility
from Sources.oazix.CustomBehaviors.skills.botting.wait_if_party_member_needs_to_loot import WaitIfPartyMemberNeedsToLootUtility
from Sources.oazix.CustomBehaviors.skills.botting.wait_if_party_member_too_far import WaitIfPartyMemberTooFarUtility

Vanquish_Path:list[tuple[float, float]] = [
      (-13384.42, -9866.60), #snake yetis  
      (-17490.23, -10193.84), #tendril
      (-13498.94, -4763.97),
      (-11674.48, -4599.29), #wallow patrol
      (-14406.66, -2555.92), #hole
      (-13735.23, -1511.41), #exit hole
      (-10319.44, 2159.07), #cave entrance
      (-7937.16, 3062.79), #wallow patrol
      (-9173.34, 7675.70),
      (-8041.39, 8370.92),
      (-4787.85, 6801.43), #clear
      (-3314.36, 7860.74),
      (-2001.17, 9037.19),
      (-6694.74, 2240.26), #out of cave
      (-9176.05, -13.35),
      (-6789.09, 189.53), #just in case
      (-6890.70, -3249.73), #lower wallows
      (-8307.69, -5465.48),
      (-5021.97, -3830.00),
      (-2310.74, -8512.54),
      (1983.03, -8555.85), #lower oxix
      (6484.80, 1017.07), #wallow patrol
      (6212.15, -8736.39), #beach onis
      (11368.18, -7458.21), #beach patrol
      (14728.93, -9258.35),
      (14774.19, -4493.75),
      (11622.91, -4078.38),
      (13287.39, 296.37),
      (16030.41, 6932.02),
      (11591.91, 7965.41), #water
      (10822.86, 9232.65),
      (7920.46, 5972.42),
      (6274.33, 7410.21), #hill
      (5824.00, 5289.97),
      (4266.50, 5832.48),
      
      (1506.29, 1406.74), #last aptrols
      (1737.57, 1202.17),
      (4450.66, 1146.03), #just in case
      (700.20, -398.73),
      (-273.59, -2516.34),
      (95.02, -3131.64),
      (-1687.58, -3565.68),
    ]

def bot_routine(bot_instance: Botting) -> None:
    
    bot_instance.Templates.Routines.UseCustomBehaviors(
    on_player_critical_death=BottingHelpers.botting_unrecoverable_issue,
    on_party_death=BottingHelpers.botting_unrecoverable_issue,
    on_player_critical_stuck=BottingHelpers.botting_unrecoverable_issue)

    BottingFsmHelpers.SetBottingBehaviorAsAggressive(bot_instance)

    CustomBehaviorParty().set_party_is_blessing_enabled(True)
    PartyFollowingManager().set_party_following_behavior_state(FollowingBehaviorPriority.LOW_PRIORITY) 

    # we just disable all to be super speed, the farm is trivial
    BottingManager().configure_aggressive_skill(MoveToEnemyIfCloseEnoughUtility.Name, enabled=True)
    BottingManager().configure_aggressive_skill(MoveToPartyMemberIfInAggroUtility.Name,enabled=True)
    BottingManager().configure_aggressive_skill(WaitIfLockTakenUtility.Name, enabled=True)
    BottingManager().configure_aggressive_skill(WaitIfPartyMemberTooFarUtility.Name, enabled=True)
    BottingManager().configure_aggressive_skill(MoveToPartyMemberIfDeadUtility.Name, enabled=True)
    BottingManager().configure_aggressive_skill(WaitIfPartyMemberManaTooLowUtility.Name, enabled=True)
    BottingManager().configure_aggressive_skill(WaitIfPartyMemberNeedsToLootUtility.Name, enabled=True)
    BottingManager().configure_aggressive_skill(WaitIfInAggroUtility.Name, enabled=True)

    bot.States.AddHeader("MAIN_LOOP")
    bot.Map.Travel(target_map_id=389) # Mount Qinkai
    bot.Party.SetHardMode(True)
    
    bot_instance.States.AddHeader("EXIT_OUTPOST")
    bot.Move.XYAndExitMap(-5490, 13672, 200) # Mount Qinkai
    bot.Wait.ForTime(4000)

    bot_instance.States.AddHeader("BLESSING")
    
    # Check faction allegiance and get blessing if needed
    # current_luxon = Player.GetLuxonData()[0]
    # current_kurzick = Player.GetKurzickData()[0]
    
    # bot.Move.XYAndInteractNPC(-8394, -9801)
    # if current_kurzick >= current_luxon:
    #     bot.Multibox.SendDialogToTarget(0x84) # This will bribe the priest in case kurzick is greater or equal than luxon
    # bot.Multibox.SendDialogToTarget(0x86) #Get Bounty

    bot.States.AddHeader("COMBAT")
    bot.Move.FollowAutoPath(Vanquish_Path, "Kill Route")
    bot.Wait.UntilOutOfCombat()

    bot.Multibox.ResignParty()
    bot.Wait.UntilOnOutpost()

    bot_instance.States.AddHeader("END")

    # bot_instance.States.AddHeader("DONATE_FACTION_IF_NEEDED")
    # bot.Templates.Routines.PrepareForFarm(map_id_to_travel=193) # Cavalon
    # bot.Multibox.DonateFaction()
    # bot.Wait.ForTime(30000)
    bot_instance.States.JumpToStepName("[H]MAIN_LOOP_1")
    
def _on_party_wipe(bot: "Botting"):
    while Agent.IsDead(Player.GetAgentID()):
        yield from bot.Wait._coro_for_time(1000)
        if not Routines.Checks.Map.MapValid():
            # Map invalid → release FSM and exit
            bot.config.FSM.resume()
            return

    # Player revived on same map → jump to recovery step
    bot.States.JumpToStepName("[H]Start Combat_3")
    bot.config.FSM.resume()
    
def OnPartyWipe(bot: "Botting"):
    ConsoleLog("on_party_wipe", "event triggered")
    fsm = bot.config.FSM
    fsm.pause()
    fsm.AddManagedCoroutine("OnWipe_OPD", lambda: _on_party_wipe(bot))

bot = Botting("[FARM] mount qinkai")
bot.SetMainRoutine(bot_routine)

def main():
    bot.Update()
    bot.UI.draw_window()

if __name__ == "__main__":
    main()