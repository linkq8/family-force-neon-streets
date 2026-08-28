using System.Collections;
using UnityEngine;

namespace FamilyForce.Unity
{
    public sealed class CombatDirector : MonoBehaviour
    {
        private PlayerMotor player;
        private EnemyCombatant enemy;
        private GameObject companion;
        private SpriteStripAnimator companionAnimator;
        private Sprite[] companionLinkFrames;
        private float nextPlayerAction;
        private bool reviving;
        private string banner = "DEFEAT THE GRUNT";
        private float bannerUntil;

        public bool CombatActive { get; private set; }
        public int PlayerHealth { get; private set; } = 120;
        public int Score { get; private set; }

        public void Initialize(PlayerMotor playerMotor, EnemyCombatant stageEnemy,
            GameObject adamCompanion)
        {
            player = playerMotor;
            enemy = stageEnemy;
            companion = adamCompanion;
            companionAnimator = companion.GetComponent<SpriteStripAnimator>();
            companionLinkFrames = CharacterAtlasCatalog.LoadClip(CharacterAtlasCatalog.Adam, "link");
            player.Configure(this);
            SetCombatActive(false);
        }

        public void SetCombatActive(bool active)
        {
            StopAllCoroutines();
            CombatActive = active;
            reviving = false;
            enemy.gameObject.SetActive(active);
            companion.SetActive(false);
            if (active)
            {
                PlayerHealth = 120;
                Score = 0;
                banner = "FIGHT!  GRAB + TEAM COMBO";
                bannerUntil = Time.time + 2.2f;
                enemy.ResetEncounter();
            }
            else
                TouchInputOverlay.SetTeamReady(false);
        }

        public bool TryPlayerAction(CombatAction action)
        {
            if (!CombatActive || Time.time < nextPlayerAction)
                return false;

            float cooldown = action == CombatAction.Heavy || action == CombatAction.Special
                ? 0.52f : 0.28f;
            nextPlayerAction = Time.time + cooldown;

            if (action == CombatAction.Grab)
            {
                bool grabbed = enemy.TryGrab();
                ShowBanner(grabbed ? "GRAB!  TEAM IS READY" : "MOVE CLOSER TO GRAB", 1.1f);
                Debug.Log($"FF_COMBAT: grab success={grabbed}");
                return true;
            }
            if (action == CombatAction.Team)
            {
                if (!enemy.IsGrabbed)
                {
                    ShowBanner("GRAB THE ENEMY FIRST", 1.1f);
                    return false;
                }
                StartCoroutine(TeamCombo());
                Debug.Log("FF_COMBAT: team combo accepted");
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
            if (enemy.IsAlive && Vector2.Distance(player.transform.position, enemy.transform.position) <= range)
            {
                enemy.TakeHit(damage, damage * 0.012f);
                Score += damage * 10;
                Debug.Log($"FF_COMBAT: hit action={action} damage={damage} enemyHp={enemy.Health}");
            }
            return true;
        }

        public void DamagePlayer(int damage)
        {
            if (!CombatActive || reviving)
                return;
            PlayerHealth = Mathf.Max(0, PlayerHealth - damage);
            player.PlayHurt();
            if (PlayerHealth == 0)
            {
                reviving = true;
                StartCoroutine(RevivePlayer());
            }
        }

        public void EnemyDefeated()
        {
            Score += 1000;
            Debug.Log($"FF_COMBAT: wave clear score={Score}");
            ShowBanner("WAVE CLEAR!  +1000", 2f);
            StartCoroutine(RestartEncounter());
        }

        private IEnumerator TeamCombo()
        {
            Vector3 enemyPosition = enemy.transform.position;
            companion.transform.position = enemyPosition + new Vector3(1.05f, 0f, 0f);
            companion.SetActive(true);
            companionAnimator.PlayOnce(companionLinkFrames);
            enemy.ApplyTeamCombo();
            Score += 750;
            ShowBanner("FAMILY TEAM COMBO!  +750", 1.5f);
            yield return new WaitForSeconds(0.9f);
            companion.SetActive(false);
        }

        private IEnumerator RestartEncounter()
        {
            yield return new WaitForSeconds(2.3f);
            if (!CombatActive)
                yield break;
            enemy.ResetEncounter();
            ShowBanner("NEXT GRUNT", 1.2f);
        }

        private IEnumerator RevivePlayer()
        {
            ShowBanner("ESSA DOWN — REVIVING", 1.5f);
            yield return new WaitForSeconds(1.5f);
            if (!CombatActive)
                yield break;
            PlayerHealth = 120;
            reviving = false;
            ShowBanner("BACK IN THE FIGHT", 1.2f);
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
                fontSize = 28,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter,
                normal = { textColor = Color.white }
            };
            DrawBar(new Rect(44f, 126f, 500f, 38f), PlayerHealth / 120f,
                new Color(0.2f, 0.9f, 0.65f), $"ESSA  HP {PlayerHealth}/120", label);
            DrawBar(new Rect(1376f, 126f, 500f, 38f), enemy.Health / (float)EnemyCombatant.MaxHealth,
                new Color(1f, 0.3f, 0.32f), $"GRUNT  HP {enemy.Health}/100", label);
            GUI.Box(new Rect(760f, 34f, 400f, 64f), $"SCORE  {Score:000000}", label);
            if (Time.time < bannerUntil)
                GUI.Box(new Rect(610f, 165f, 700f, 62f), banner, label);
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
