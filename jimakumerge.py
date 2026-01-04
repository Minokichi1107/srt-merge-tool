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
