# 합성 carbon intensity 데이터 생성
import json, random
regions = ["KR","JP","US","EU"]
H = 96  # 15분 단위 하루
out = {r: [random.randint(250, 500) for _ in range(H)] for r in regions}
open("sims/ci_day.json","w").write(json.dumps(out, indent=2))
print("✅ wrote sims/ci_day.json")
