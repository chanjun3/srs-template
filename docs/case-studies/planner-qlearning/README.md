# 🧭 Planner Agent × Q-learning 統合レポート

## 1️⃣ 背景と目的

Planner Agentは、複数のサブエージェント（Designer, Coder, Deployerなど）を統括し、
「どのタスクを・どの順番で・どのリソースを使って実行するか」を決定する中核的存在。
これを静的ルール（if-then）ではなく**学習型意思決定**に変えることで、
プロジェクト進行の最適化を継続的に行う狙いがある。

---

## 2️⃣ Q-learningの基礎

Q-learningは、**状態(s)** と **行動(a)** の組み合わせに対して「将来の報酬期待値Q(s,a)」を学習する強化学習アルゴリズム。
環境モデルを必要とせず、観測された報酬に基づいて方策を改善していく。

\[
Q(s,a) \leftarrow Q(s,a) + \alpha [r + \gamma \max_{a'} Q(s',a') - Q(s,a)]
\]

---

## 3️⃣ Planner Agentへの適用設計

### 🧩 状態（State）

```python
state = {
  "task_progress": completion_ratio,
  "agent_load": avg_cpu_usage,
  "priority_level": project_priority,
  "deadline_gap": remaining_days,
  "reward_history": recent_reward_avg
}
```

### ⚙️ 行動（Action）

```python
actions = [
  "delegate_to_coder",
  "delegate_to_designer",
  "wait_for_feedback",
  "reprioritize_task",
  "request_external_api"
]
```

### 🎯 報酬（Reward）

評価基準    報酬スコア例
タスク成功    +1.0
納期遅延なし    +0.5
エラー発生    -1.0
再実行必要    -0.5
他エージェント支援成功    +0.8

## 4️⃣ 実装構造

```text
planner_agent/
 ├─ q_learning/
 │   ├─ q_table.py
 │   ├─ policy.py
 │   └─ reward_model.py
 ├─ environment.py
 ├─ planner_core.py
 └─ memory/q_memory.json
```

## 5️⃣ 学習ループ

```python
for episode in range(max_episodes):
    state = env.reset()
    done = False
    while not done:
        action = policy.select_action(state)
        next_state, reward, done = env.step(action)
        q_table.update(state, action, reward, next_state)
        state = next_state
```

## 6️⃣ 効果とリスク

### 💡 効果

タスク優先度の自動最適化

過去の失敗パターンからの自己修正

マルチエージェント間の協調学習（Federated Q-learning化）

### ⚠️ リスク

探索行動による初期非効率

報酬スパース環境での停滞

意思決定基準のブラックボックス化

## 7️⃣ 強化ポイント

視点    提案
報酬構造    GPT評価やNotion DBの成功ログから自動スコア化
知識共有    Planner間でQテーブルをFederated同期
安定性    Experience Replayで再学習
透明性    Q値をGrafanaで可視化
メタ制御    Orchestratorが学習率αを自動調整

## 8️⃣ LLM × Q-learning の融合

LLMは「タスクの意味理解」に強く、
Q-learningは「行動の最適化」に強い。
両者を組み合わせることで、
“理解して動く自己最適化エージェント”が実現する。

## 9️⃣ 理論的根拠

Sutton & Barto, Reinforcement Learning: An Introduction (2018)

Silver et al., Mastering the Game of Go (Nature, 2016)

DeepMind, Hierarchical RL in Multi-Agent Systems (2021)

## 🔟 次アクション

ステップ    内容    成果物
①    Q-table構造の定義    q_table.py
②    Reward関数作成    reward_model.py
③    ε-greedy探索の実装    policy.py
④    PlannerCoreにhook統合    planner_core.py
⑤    学習ログをNotion連携    planner_learning_log.md

## Reference

- docs/spec_os/srs.md
