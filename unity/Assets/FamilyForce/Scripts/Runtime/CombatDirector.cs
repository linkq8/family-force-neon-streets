using System;
using System.Collections;
using UnityEngine;

namespace FamilyForce.Unity
{
    public sealed class CombatDirector : MonoBehaviour
    {
        private readonly int[] playerHealth = { 120, 110 };
        private readonly bool[] reviving = new bool[2];
        private readonly float[] nextPlayerAction = new float[2];
        private readonly int[] punchStep = new int[2];
        private readonly float[] comboUntil = new float[2];
        private PlayerMotor playerOne;
        private PlayerMotor playerTwo;
        private EnemyCombatant enemy;
        private WeaponPickup weapon;
        private string banner = "STAGE 1 — NEON MARKET";
        private float bannerUntil;
        private int encounter;
        private float stageStartedAt;
        private bool hitStopActive;

        public bool CombatActive { get; private set; }
        public bool TwoPlayers { get; private set; }
        public int Score { get; private set; }
        public int EncounterNumber => encounter + 1;
        public event Action<int, float> StageCompleted;

        public void Initialize(PlayerMotor p1, PlayerMotor p2, EnemyCombatant stageEnemy,
            WeaponPickup stageWeapon)
        {
            playerOne = p1;
            playerTwo = p2;
            enemy = stageEnemy;
            weapon = stageWeapon;
            playerOne.Configure(this, CharacterAtlasCatalog.Essa, 0, true);
            playerTwo.Configure(this, CharacterAtlasCatalog.Adam, 1, false);
            SetCombatActive(false, false);
        }

        public void SelectCharacters(string p1Actor, string p2Actor)
        {
            playerOne.SelectActor(p1Actor);
            playerTwo.SelectActor(p2Actor);
        }

        public void SetCombatActive(bool active, bool enableP2)
        {
            StopAllCoroutines();
            Time.timeScale = 1f;
            hitStopActive = false;
            CombatActive = active;
            TwoPlayers = active && enableP2;
            for (int i = 0; i < 2; i++)
            {
                reviving[i] = false;
                nextPlayerAction[i] = 0f;
                punchStep[i] = 0;
                comboUntil[i] = 0f;
            }
            enemy.gameObject.SetActive(false);
            playerOne.gameObject.SetActive(active);
            playerTwo.gameObject.SetActive(TwoPlayers);
            weapon.gameObject.SetActive(false);
            playerOne.SetControlEnabled(false);
            playerTwo.SetControlEnabled(false);
            if (active)
            {
                playerHealth[0] = playerOne.ActorName == CharacterAtlasCatalog.Adam ? 110 : 120;
                playerHealth[1] = playerTwo.ActorName == CharacterAtlasCatalog.Adam ? 110 : 120;
                Score = 0;
                encounter = 0;
                stageStartedAt = Time.unscaledTime;
                playerOne.ResetPosition(new Vector3(-4f, -2.15f, 0f));
                playerTwo.ResetPosition(new Vector3(-5.1f, -2.65f, 0f));
                StartCoroutine(StageIntro());
            }
            else
            {
                TouchInputOverlay.SetTeamReady(false);
                TouchInputOverlay.SetWeaponHeld(false);
            }
        }

        private IEnumerator StageIntro()
        {
            ShowBanner("STAGE 1 — NEON MARKET", 1.4f);
            yield return new WaitForSecondsRealtime(1.45f);
            ShowBanner("ROBOT NETWORK BREACH DETECTED", 1.25f);
            yield return new WaitForSecondsRealtime(1.3f);
            ShowBanner("FAMILY FORCE — GO!", 0.9f);
            playerOne.SetControlEnabled(true);
            playerTwo.SetControlEnabled(TwoPlayers);
            SpawnCurrentEncounter();
        }

        private void SpawnCurrentEncounter()
        {
            if (!CombatActive)
                return;
            if (encounter < 3)
            {
                enemy.Spawn(CharacterAtlasCatalog.Grunt, $"GRUNT {encounter + 1}",
                    90 + encounter * 15, 1.45f + encounter * 0.08f, 7 + encounter,
                    new Vector3(3.2f, -2.15f + encounter * 0.22f, 0f), 3.05f);
                ShowBanner($"WAVE {encounter + 1}/3", 1f);
                if (encounter == 0)
                    weapon.ResetPickup(new Vector3(0.25f, -2.15f, 0f));
            }
            else
            {
                enemy.Spawn(CharacterAtlasCatalog.MarketEnforcer, "MARKET ENFORCER",
                    260, 1.28f, 13, new Vector3(3.35f, -2.0f, 0f), 3.0f);
                ShowBanner("MINI-BOSS — MARKET ENFORCER", 1.8f);
            }
        }

        public bool TryPlayerAction(PlayerMotor actor, CombatAction action)
        {
            int index = actor.PlayerIndex;
            if (!CombatActive || index < 0 || index > 1 || !actor.gameObject.activeInHierarchy
                || reviving[index] || Time.unscaledTime < nextPlayerAction[index])
                return false;

            if (action == CombatAction.Weapon)
            {
                if (weapon.Owner == actor)
                    return SwingWeapon(actor, index);
                bool picked = weapon.TryPickup(actor);
                ShowBanner(picked ? "BAT ACQUIRED — EAST TO SWING" : "MOVE CLOSER TO THE BAT", 1f);
                return picked;
            }
            if (action == CombatAction.Throw)
            {
                if (weapon.Owner != actor)
                    return false;
                weapon.Throw(actor);
                nextPlayerAction[index] = Time.unscaledTime + 0.35f;
                ShowBanner("WEAPON THROW!", 0.7f);
                return true;
            }

            if (TwoPlayers && enemy.IsGrabbed && enemy.Grabber != actor
                && (action == CombatAction.Punch || action == CombatAction.Team))
                action = CombatAction.Team;
            float cooldown = action == CombatAction.Heavy || action == CombatAction.Special
                ? 0.52f : 0.28f;
            nextPlayerAction[index] = Time.unscaledTime + cooldown;

            if (action == CombatAction.Grab)
            {
                bool grabbed = enemy.TryGrab(actor);
                ShowBanner(grabbed
                    ? TwoPlayers ? "GRAB! OTHER PLAYER: ATTACK" : "GRAB! TEAM IS READY"
                    : "MOVE CLOSER TO GRAB", 1.1f);
                return true;
            }
            if (action == CombatAction.Team)
            {
                if (!enemy.IsGrabbed || (TwoPlayers && enemy.Grabber == actor))
                {
                    ShowBanner(enemy.IsGrabbed ? "WAIT FOR THE OTHER PLAYER" : "GRAB THE ENEMY FIRST", 1.1f);
                    return false;
                }
                if (TwoPlayers && Vector2.Distance(actor.transform.position, enemy.transform.position) > 2.2f)
                {
                    ShowBanner("PARTNER: MOVE CLOSER", 1.1f);
                    return false;
                }
                StartCoroutine(TeamCombo(actor));
                return true;
            }

            int damage;
            if (action == CombatAction.Punch)
            {
                punchStep[index] = Time.unscaledTime <= comboUntil[index] ? (punchStep[index] % 3) + 1 : 1;
                comboUntil[index] = Time.unscaledTime + 0.7f;
                damage = punchStep[index] == 3 ? 18 : 9 + punchStep[index] * 2;
            }
            else
                damage = action switch
                {
                    CombatAction.Kick => 14,
                    CombatAction.Heavy => 22,
                    CombatAction.Special => 30,
                    _ => 0
                };
            float range = action == CombatAction.Special ? 2.25f : 1.75f;
            if (enemy.IsAlive && enemy.Hurtbox.OverlapsAttack(actor.transform.position,
                actor.FacingRight, range))
            {
                enemy.TakeHit(damage, damage * 0.012f, actor.transform);
                Score += damage * 10;
                StartCoroutine(HitStop(action == CombatAction.Heavy ? 0.075f : 0.045f));
            }
            return true;
        }

        private bool SwingWeapon(PlayerMotor actor, int index)
        {
            nextPlayerAction[index] = Time.unscaledTime + 0.48f;
            if (enemy.IsAlive && enemy.Hurtbox.OverlapsAttack(actor.transform.position,
                actor.FacingRight, 2.05f))
            {
                enemy.TakeHit(26, 0.55f, actor.transform);
                Score += 320;
                StartCoroutine(HitStop(0.075f));
            }
            return true;
        }

        private void Update()
        {
            if (CombatActive && weapon.CanHitThrown(enemy))
            {
                weapon.MarkThrownHit();
                enemy.TakeHit(34, 0.85f, weapon.transform);
                Score += 420;
                StartCoroutine(HitStop(0.08f));
            }
        }

        private IEnumerator HitStop(float seconds)
        {
            if (hitStopActive)
                yield break;
            hitStopActive = true;
            Time.timeScale = 0.08f;
            yield return new WaitForSecondsRealtime(seconds);
            Time.timeScale = 1f;
            hitStopActive = false;
        }

        public PlayerMotor ClosestActivePlayer(Vector3 from)
        {
            if (!TwoPlayers || !playerTwo.gameObject.activeInHierarchy || reviving[1])
                return playerOne;
            if (reviving[0])
                return playerTwo;
            return Vector2.SqrMagnitude(playerOne.transform.position - from)
                <= Vector2.SqrMagnitude(playerTwo.transform.position - from) ? playerOne : playerTwo;
        }

        public void DamagePlayer(PlayerMotor target, int damage)
        {
            int index = target.PlayerIndex;
            if (!CombatActive || index < 0 || index > 1 || reviving[index])
                return;
            playerHealth[index] = Mathf.Max(0, playerHealth[index] - damage);
            target.PlayHurt();
            if (playerHealth[index] == 0)
            {
                reviving[index] = true;
                StartCoroutine(RevivePlayer(target));
            }
        }

        public void EnemyDefeated()
        {
            Score += encounter == 3 ? 5000 : 1000;
            StartCoroutine(AdvanceEncounter());
        }

        private IEnumerator AdvanceEncounter()
        {
            ShowBanner(encounter == 3 ? "MINI-BOSS DEFEATED!" : "WAVE CLEAR!", 1.5f);
            yield return new WaitForSecondsRealtime(1.65f);
            if (!CombatActive)
                yield break;
            encounter++;
            if (encounter > 3)
            {
                playerOne.SetControlEnabled(false);
                playerTwo.SetControlEnabled(false);
                ShowBanner("STAGE CLEAR!", 2f);
                yield return new WaitForSecondsRealtime(2f);
                StageCompleted?.Invoke(Score, Time.unscaledTime - stageStartedAt);
                yield break;
            }
            SpawnCurrentEncounter();
        }

        private IEnumerator TeamCombo(PlayerMotor partner)
        {
            PlayerMotor grabber = enemy.Grabber;
            bool usingAiCompanion = !TwoPlayers;
            if (usingAiCompanion)
            {
                partner = playerTwo;
                partner.ResetPosition(enemy.transform.position + new Vector3(1.05f, 0f, 0f));
                partner.gameObject.SetActive(true);
            }
            grabber?.PlayTeamAction();
            partner.PlayTeamAction();
            enemy.ApplyTeamCombo();
            Score += 750;
            ShowBanner("FAMILY TEAM COMBO! +750", 1.5f);
            yield return new WaitForSecondsRealtime(0.9f);
            if (usingAiCompanion)
                playerTwo.gameObject.SetActive(false);
        }

        private IEnumerator RevivePlayer(PlayerMotor target)
        {
            int index = target.PlayerIndex;
            ShowBanner($"P{index + 1} DOWN — REVIVING", 1.5f);
            target.gameObject.SetActive(false);
            yield return new WaitForSecondsRealtime(1.5f);
            if (!CombatActive || (index == 1 && !TwoPlayers))
                yield break;
            playerHealth[index] = target.ActorName == CharacterAtlasCatalog.Adam ? 110 : 120;
            reviving[index] = false;
            target.ResetPosition(index == 0 ? new Vector3(-4f, -2.15f, 0f) : new Vector3(-5.1f, -2.65f, 0f));
            target.gameObject.SetActive(true);
            ShowBanner($"P{index + 1} BACK IN THE FIGHT", 1.2f);
        }

        private void ShowBanner(string text, float seconds)
        {
            banner = text;
            bannerUntil = Time.unscaledTime + seconds;
        }

        private void OnGUI()
        {
            if (!CombatActive)
                return;
            GUI.matrix = Matrix4x4.Scale(new Vector3(Screen.width / 1920f, Screen.height / 1080f, 1f));
            GUIStyle label = new GUIStyle(GUI.skin.box) { fontSize = 26, fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter, normal = { textColor = Color.white } };
            int p1Max = playerOne.ActorName == CharacterAtlasCatalog.Adam ? 110 : 120;
            int p2Max = playerTwo.ActorName == CharacterAtlasCatalog.Adam ? 110 : 120;
            DrawBar(new Rect(44f, 112f, 500f, 36f), playerHealth[0] / (float)p1Max,
                new Color(0.2f, 0.9f, 0.65f), $"P1 {playerOne.ActorName.ToUpperInvariant()}  {playerHealth[0]}/{p1Max}", label);
            if (TwoPlayers)
                DrawBar(new Rect(44f, 154f, 500f, 36f), playerHealth[1] / (float)p2Max,
                    new Color(0.35f, 0.85f, 0.25f), $"P2 {playerTwo.ActorName.ToUpperInvariant()}  {playerHealth[1]}/{p2Max}", label);
            if (enemy.gameObject.activeInHierarchy)
                DrawBar(new Rect(1376f, 112f, 500f, 36f), enemy.Health / (float)enemy.MaxHealth,
                    new Color(1f, 0.3f, 0.32f), $"{enemy.DisplayName}  {enemy.Health}/{enemy.MaxHealth}", label);
            GUI.Box(new Rect(760f, 34f, 400f, 64f), $"SCORE  {Score:000000}", label);
            if (Time.unscaledTime < bannerUntil)
                GUI.Box(new Rect(610f, 150f, 700f, 62f), banner, label);
        }

        private static void DrawBar(Rect rect, float value, Color color, string text, GUIStyle style)
        {
            GUI.Box(rect, GUIContent.none);
            Color previous = GUI.color;
            GUI.color = color;
            GUI.Box(new Rect(rect.x + 4f, rect.y + 4f, (rect.width - 8f) * Mathf.Clamp01(value), rect.height - 8f), GUIContent.none);
            GUI.color = previous;
            GUI.Label(rect, text, style);
        }
    }
}
