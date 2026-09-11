using UnityEngine;

namespace FamilyForce.Unity
{
    /// <summary>Deterministic Sprite Atlas clip player, independent of render FPS.</summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public sealed class SpriteStripAnimator : MonoBehaviour
    {
        private const float AnimationFps = 12f;

        private SpriteRenderer target;
        private Sprite[] idleFrames;
        private Sprite[] walkFrames;
        private Sprite[] actionFrames;
        private float accumulator;
        private int frame;
        private bool moving;
        private bool actionPlaying;
        private float walkRate = 1f;
        private float[] actionDurations;
        private float[] idleDurations, walkDurations;
        private bool holdActionEnd;
        private bool showMotionDebug;
        private int savedWalkFrame;
        private float savedWalkAccumulator;
        private string lastLoggedSprite;
        private int renderedUnityFrame=-1, submitted, changed;
        private float sampleStarted;
        private string previousSubmittedSprite="", renderSummary="Waiting for render sample";

        public bool IsPlayingAction => actionPlaying;
        public bool IsMoving => moving;
        public int CurrentFrame => frame;
        public int CurrentFrameCount => CurrentFrames()?.Length ?? 0;
        public string CurrentSpriteName => target != null && target.sprite != null ? target.sprite.name : "";

        public void SetWalkRate(float value) => walkRate = Mathf.Clamp(value, 0.1f, 2.5f);

        private void OnEnable(){sampleStarted=0;submitted=changed=0;renderedUnityFrame=-1;previousSubmittedSprite="";}

        public void Initialize(Sprite[] idle, Sprite[] walk, float[] idleTiming = null, float[] walkTiming = null)
        {
            target = GetComponent<SpriteRenderer>();
            if (idle == null || idle.Length == 0)
            {
                Debug.LogError("FF_UNITY: missing idle clip in Sprite Atlas");
                return;
            }
            idleFrames = idle;
            walkFrames = walk != null && walk.Length > 0 ? walk : idle;
            idleDurations = idleTiming != null && idleTiming.Length == idleFrames.Length ? idleTiming : null;
            walkDurations = walkTiming != null && walkTiming.Length == walkFrames.Length ? walkTiming : null;
            holdActionEnd = false;
            moving = actionPlaying = false;
            actionFrames = null;
            actionDurations = null;
            walkRate = 1f;
            savedWalkFrame = 0;
            savedWalkAccumulator = 0f;
            frame = 0;
            accumulator = 0f;
            ApplyFrame();
            Debug.Log($"FF_UNITY: atlas sprite initialized idle={idleFrames.Length} " +
                $"walk={walkFrames.Length} sprite={(target.sprite != null)}");
        }

        public void SetMoving(bool value)
        {
            if (moving == value)
                return;
            if (moving && !actionPlaying) SaveWalkPosition();
            moving = value;
            if (actionPlaying)
                return;
            frame = moving ? savedWalkFrame : 0;
            accumulator = moving ? savedWalkAccumulator : 0f;
            ApplyFrame();
        }

        public bool PlayOnce(Sprite[] frames, float[] durations = null, bool holdLast = false)
        {
            if (frames == null || frames.Length == 0)
                return false;
            if (moving && !actionPlaying) SaveWalkPosition();
            actionFrames = frames;
            actionDurations = durations != null && durations.Length == frames.Length ? durations : null;
            actionPlaying = true;
            holdActionEnd = holdLast;
            frame = 0;
            accumulator = 0f;
            ApplyFrame();
            return true;
        }

        private void Update()
        {
            if (gameObject.name == "P1_Essa")
            {
                bool toggle = Input.GetKeyDown(KeyCode.F8);
                if (Input.touchCount == 3)
                    for (int i=0;i<3;i++) toggle |= Input.GetTouch(i).phase == TouchPhase.Began;
                if (toggle) showMotionDebug = !showMotionDebug;
            }
            Advance(Time.deltaTime);
        }

        private void SaveWalkPosition()
        {
            savedWalkFrame = frame;
            savedWalkAccumulator = accumulator;
        }

        private void Advance(float deltaTime)
        {
            accumulator += Mathf.Max(0f, deltaTime);
            while (accumulator >= FrameDuration())
            {
                accumulator -= FrameDuration();
                Sprite[] frames = CurrentFrames();
                if (frames == null || frames.Length == 0)
                    continue;
                if (actionPlaying && frame + 1 >= frames.Length)
                {
                    if (holdActionEnd) { accumulator = 0; break; }
                    actionPlaying = false;
                    actionFrames = null;
                    actionDurations = null;
                    // Resume the interrupted gait instead of starving its second half
                    // whenever an enemy hit, punch or brief touch release occurs.
                    frame = moving ? savedWalkFrame : 0;
                    if (moving) accumulator += savedWalkAccumulator;
                }
                else
                    frame = (frame + 1) % frames.Length;
                ApplyFrame();
            }
        }

        public void StopAction()
        {
            actionPlaying = holdActionEnd = false; actionFrames = null; actionDurations = null;
            frame = moving ? savedWalkFrame : 0; accumulator = moving ? savedWalkAccumulator : 0;
            ApplyFrame();
        }

        private float FrameDuration()
        {
            var timing = actionPlaying ? actionDurations : moving ? walkDurations : idleDurations;
            float seconds = timing != null ? timing[Mathf.Clamp(frame,0,timing.Length-1)] : 1f/AnimationFps;
            return Mathf.Max(.016f,seconds/(!actionPlaying && moving ? walkRate : 1f));
        }

        private void ApplyFrame()
        {
            Sprite[] frames = CurrentFrames();
            if (target != null && frames != null && frames.Length > 0)
            {
                target.sprite = frames[Mathf.Clamp(frame, 0, frames.Length - 1)];
                if (showMotionDebug && lastLoggedSprite != target.sprite.name)
                {
                    Debug.Log($"FF_MOTION_FRAME {target.sprite.name} {frame+1}/{frames.Length}");
                    lastLoggedSprite = target.sprite.name;
                }
            }
        }

        private void OnGUI()
        {
            if (showMotionDebug)
                GUI.Box(new Rect(12,142,420,70),$"{CurrentSpriteName}  {frame+1}/{CurrentFrameCount}\n{renderSummary}\nF8 / 3 fingers: hide");
        }

        // Count camera submissions, not Advance's intermediate poses. Physical
        // display presentation still requires video QA on the user's device.
        private void OnWillRenderObject()
        {
            if(gameObject.name!="P1_Essa" || Camera.current!=Camera.main || renderedUnityFrame==Time.frameCount)return;
            renderedUnityFrame=Time.frameCount;
            float now=Time.unscaledTime;if(sampleStarted==0)sampleStarted=now;
            submitted++;
            if(previousSubmittedSprite!=CurrentSpriteName){changed++;previousSubmittedSprite=CurrentSpriteName;}
            if(now-sampleStarted>=1f)
            {
                float seconds=now-sampleStarted;
                renderSummary=$"Render {submitted/seconds:0} FPS | poses {changed/seconds:0}/s";
                Debug.Log($"FF_RENDER {renderSummary} sprite={CurrentSpriteName} frame={frame+1}/{CurrentFrameCount} moving={moving}");
                sampleStarted=now;submitted=changed=0;
            }
        }

        private Sprite[] CurrentFrames() => actionPlaying && actionFrames != null
            ? actionFrames
            : moving ? walkFrames : idleFrames;
    }
}
