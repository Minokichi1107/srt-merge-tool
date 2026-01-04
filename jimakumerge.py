def parse_srt(path):
    subs = []
    with open(path, encoding="utf-8") as f:
        block = []
        for line in f:
            line = line.strip()
            if line == "":
                if len(block) >= 3:
                    time = block[1]
                    text = " ".join(block[2:])
                    start = to_seconds(time.split(" --> ")[0])
                    subs.append((start, time, text))
                block = []
            else:
                block.append(line)

        # 最後のブロック対策
        if len(block) >= 3:
            time = block[1]
            text = " ".join(block[2:])
            start = to_seconds(time.split(" --> ")[0])
            subs.append((start, time, text))

    return subs


def to_seconds(t):
    h, m, rest = t.split(":")

    if "," in rest:
        s, ms = rest.split(",")
    elif "." in rest:
        s, ms = rest.split(".")
    else:
        s = rest
        ms = "0"

    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000


def merge(jpn, eng, threshold=0.5, carry_threshold=0.8):
    result = []
    used = set()
    leftovers = []

    for idx, (j_start, j_time, j_text) in enumerate(jpn):
        closest = None
        closest_diff = threshold

        for i, (e_start, e_time, e_text) in enumerate(eng):
            if i in used:
                continue
            diff = abs(j_start - e_start)
            if diff < closest_diff:
                closest = (i, e_text, e_start)
                closest_diff = diff

        if closest:
            used.add(closest[0])
            result.append({
                "time": j_time,
                "eng": closest[1],
                "jpn": j_text,
                "start": j_start
            })
        else:
            result.append({
                "time": j_time,
                "eng": "",
                "jpn": j_text,
                "start": j_start
            })

    # 使われなかった英語を回収
    for i, (e_start, e_time, e_text) in enumerate(eng):
        if i not in used:
            leftovers.append((e_start, e_time, e_text))

    # 後処理
    for e_start, e_time, e_text in leftovers:
        inserted = False
        for block in result:
            diff = abs(block["start"] - e_start)
            if diff < carry_threshold:
                block["eng"] = e_text + " " + block["eng"]
                inserted = True
                break

        if not inserted:
            result.append({
                "time": e_time,
                "eng": e_text,
                "jpn": "",
                "start": e_start
            })

    # 時間順に並べ直し
    result.sort(key=lambda x: x["start"])

    return result



# ==== ここだけ自分の環境に合わせて変更 ====
jpn_srt = "japanese.srt"
eng_srt = "english.srt"
out_srt = "merged.srt"

jpn = parse_srt(jpn_srt)
eng = parse_srt(eng_srt)

merged = merge(jpn, eng)

with open(out_srt, "w", encoding="utf-8") as f:
    for i, block in enumerate(merged, 1):
        f.write(f"{i}\n")
        f.write(f"{block['time']}\n")
        if block["eng"]:
            f.write(block["eng"] + "\n")
        if block["jpn"]:
            f.write(block["jpn"] + "\n")
        f.write("\n")


print("結合完了")
