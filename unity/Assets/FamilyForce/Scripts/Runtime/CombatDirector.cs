using System.Collections;
using UnityEngine;

namespace FamilyForce.Unity
{
    public sealed class CombatDirector : MonoBehaviour
    {
        private readonly int[] playerHealth = { 120, 110 };
        private readonly bool[] reviving = new bool[2];
        private readonly float[] nextPlayerAction = new float[2];
        private PlayerMotor playerOne;
        private PlayerMotor playerTwo;
        private EnemyCombatant enemy;
        private string banner = "DEFEAT THE GRUNT";
        private float bannerUntil;

        public bool CombatActive { get; private set; }
        public bool TwoPlayers { get; private set; }
        public int Score { get; private set; }

        public void Initialize(PlayerMotor p1, PlayerMotor p2, EnemyCombatant stageEnemy)
        {
            playerOne = p1;
            playerTwo = p2;
            enemy = stageEnemy;
            playerOne.Configure(this, CharacterAtlasCatalog.Essa, 0, true);
            playerTwo.Configure(this, CharacterAtlasCatalog.Adam, 1, false);
            SetCombatActive(false, false);
        }

        public void SetCombatActive(bool active, bool enableP2)
        {
            StopAllCoroutines();
            CombatActive = active;
            TwoPlayers = active && enableP2;
            reviving[0] = false;
            reviving[1] = false;
            nextPlayerAction[0] = 0f;
            nextPlayerAction[1] = 0f;
            enemy.gameObject.SetActive(active);
            playerOne.gameObject.SetActive(active);
            playerTwo.gameObject.SetActive(TwoPlayers);
            if (active)
            {
                playerHealth[0] = 120;
                playerHealth[1] = 110;
                Score = 0;
                playerOne.ResetPosition(new Vector3(-4f, -2.15f, 0f));
                playerTwo.ResetPosition(new Vector3(-5.1f, -2.65f, 0f));
                banner = TwoPlayers
                    ? "2 PLAYERS — GRAB, THEN PARTNER ATTACKS"
                    : "1 PLAYER — GRAB + TEAM COMBO";
                bannerUntil = Time.time + 2.4f;
                enemy.ResetEncounter();
            }
            else
                TouchInputOverlay.SetTeamReady(false);
        }

        public bool TryPlayerAction(PlayerMotor actor, CombatAction action)
        {
            int index = actor.PlayerIndex;
            if (!CombatActive || index < 0 || index > 1 || !actor.gameObject.activeInHierarchy
                || reviving[index] || Time.time < nextPlayerAction[index])
                return false;

            if (TwoPlayers && enemy.IsGrabbed && enemy.Grabber != actor
                && (action == CombatAction.Punch || action == CombatAction.Team))
                action = CombatAction.Team;

            float cooldown = action == CombatAction.Heavy || action == CombatAction.Special
                ? 0.52f : 0.28f;
            nextPlayerAction[index] = Time.time + cooldown;

            if (action == CombatAction.Grab)
            {
                bool grabbed = enemy.TryGrab(actor);
                ShowBanner(grabbed
                    ? TwoPlayers ? "GRAB!  OTHER PLAYER: ATTACK" : "GRAB!  TEAM IS READY"
                    : "MOVE CLOSER TO GRAB", 1.1f);
                Debug.Log($"FF_COMBAT: p{index + 1} grab success={grabbed}");
                return true;
            }
            if (action == CombatAction.Team)
            {
                if (!enemy.IsGrabbed)
                {
                    ShowBanner("GRAB THE ENEMY FIRST", 1.1f);
                    return false;
                }
                if (TwoPlayers && enemy.Grabber == actor)
                {
                    ShowBanner("WAIT FOR THE OTHER PLAYER", 1.1f);
                    return false;
                }
                if (TwoPlayers && Vector2.Distance(actor.transform.position, enemy.transform.position) > 2.2f)
                {
                    ShowBanner("PARTNER: MOVE CLOSER", 1.1f);
                    return false;
                }
                StartCoroutine(TeamCombo(actor));
                Debug.Log($"FF_COMBAT: team combo accepted by p{index + 1}");
                return true;
            }

            int damage = action switch
            {
                CombatAction.Punch => 10,
                CombatAction.Kick => 14,
                CombatAction.Heavy => 22,
                CombatAction.Special => 30,
                _ => 0
            };
            float range = action == CombatAction.Special ? 2.25f : 1.7f;
            if (enemy.IsAlive && Vector2.Distance(actor.transform.position, enemy.transform.position) <= range)
            {
                enemy.TakeHit(damage, damage * 0.012f, actor.transform);
                Score += damage * 10;
                Debug.Log($"FF_COMBAT: p{index + 1} hit action={action} damage={damage} enemyHp={enemy.Health}");
            }
            return true;
        }

        public PlayerMotor ClosestActivePlayer(Vector3 from)
        {
            if (!TwoPlayers || !playerTwo.gameObject.activeInHierarchy || reviving[1])
                return playerOne;
            if (reviving[0])
                return playerTwo;
            return Vector2.SqrMagnitude(playerOne.transform.position - from)
                <= Vector2.SqrMagnitude(playerTwo.transform.position - from)
                ? playerOne : playerTwo;
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
            Score += 1000;
            Debug.Log($"FF_COMBAT: wave clear score={Score}");
            ShowBanner("WAVE CLEAR!  +1000", 2f);
            StartCoroutine(RestartEncounter());
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
            ShowBanner("FAMILY TEAM COMBO!  +750", 1.5f);
            yield return new WaitForSeconds(0.9f);
            if (usingAiCompanion)
                playerTwo.gameObject.SetActive(false);
        }

        private IEnumerator RestartEncounter()
        {
            yield return new WaitForSeconds(2.3f);
            if (!CombatActive)
                yield break;
            enemy.ResetEncounter();
            ShowBanner("NEXT GRUNT", 1.2f);
        }

        private IEnumerator RevivePlayer(PlayerMotor target)
        {
            int index = target.PlayerIndex;
            ShowBanner($"P{index + 1} DOWN — REVIVING", 1.5f);
            target.gameObject.SetActive(false);
            yield return new WaitForSeconds(1.5f);
            if (!CombatActive || (index == 1 && !TwoPlayers))
                yield break;
            playerHealth[index] = index == 0 ? 120 : 110;
            reviving[index] = false;
            target.ResetPosition(index == 0
                ? new Vector3(-4f, -2.15f, 0f)
                : new Vector3(-5.1f, -2.65f, 0f));
            target.gameObject.SetActive(true);
            ShowBanner($"P{index + 1} BACK IN THE FIGHT", 1.2f);
        }

        private void ShowBanner(string text, float seconds)
        {
            banner = text;
            bannerUntil = Time.time + seconds;
        }

        private void OnGUI()
        {
            if (!CombatActive)
                return;
            GUI.matrix = Matrix4x4.Scale(new Vector3(Screen.width / 1920f, Screen.height / 1080f, 1f));
            GUIStyle label = new GUIStyle(GUI.skin.box)
            {
                fontSize = 26,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter,
                normal = { textColor = Color.white }
            };
            DrawBar(new Rect(44f, 112f, 500f, 36f), playerHealth[0] / 120f,
                new Color(0.2f, 0.9f, 0.65f), $"P1 ESSA  {playerHealth[0]}/120", label);
            if (TwoPlayers)
                DrawBar(new Rect(44f, 154f, 500f, 36f), playerHealth[1] / 110f,
                    new Color(0.35f, 0.85f, 0.25f), $"P2 ADAM  {playerHealth[1]}/110", label);
            DrawBar(new Rect(1376f, 112f, 500f, 36f), enemy.Health / (float)EnemyCombatant.MaxHealth,
                new Color(1f, 0.3f, 0.32f), $"GRUNT  {enemy.Health}/100", label);
            GUI.Box(new Rect(760f, 34f, 400f, 64f), $"SCORE  {Score:000000}", label);
            if (Time.time < bannerUntil)
                GUI.Box(new Rect(610f, 150f, 700f, 62f), banner, label);
        }

        private static void DrawBar(Rect rect, float value, Color color, string text, GUIStyle style)
        {
            GUI.Box(rect, GUIContent.none);
            Color previous = GUI.color;
            GUI.color = color;
            GUI.Box(new Rect(rect.x + 4f, rect.y + 4f, (rect.width - 8f) * Mathf.Clamp01(value),
                rect.height - 8f), GUIContent.none);
            GUI.color = previous;
            GUI.Label(rect, text, style);
        }
    }
}
