import hashlib
import base64
import time
import random
import string
import urllib.parse

# ──────────────────────────────────────────────────────────────────────
# XBogus Implementation (without classes/def)
# ──────────────────────────────────────────────────────────────────────

STANDARD_B64_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
CUSTOM_B64_ALPHABET   = 'Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe'
ENC_TRANS = {s: c for s, c in zip(STANDARD_B64_ALPHABET, CUSTOM_B64_ALPHABET)}

# Custom base64 encoding
def custom_b64_encode(buf):
    b64 = base64.b64encode(buf).decode('ascii')
    return ''.join(ENC_TRANS.get(ch, ch) for ch in b64)

# MD5 encryption
def std_md5_enc(data):
    return hashlib.md5(data).digest()

# RC4 encryption
def rc4_enc(key, plaintext):
    s = list(range(256))
    j = 0
    key_len = len(key)
    for i in range(256):
        j = (j + s[i] + key[i % key_len]) & 0xFF
        s[i], s[j] = s[j], s[i]
    
    out = bytearray(len(plaintext))
    i = j = 0
    for n in range(len(plaintext)):
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        k = s[(s[i] + s[j]) & 0xFF]
        out[n] = plaintext[n] ^ k
    return bytes(out)

# XOR key
def xor_key(buf):
    acc = 0
    for b in buf:
        acc ^= b
    return acc

# XBogus encrypt
def xbogus_encrypt(params, post_data, user_agent, timestamp):
    ua_key   = bytes([0x00, 0x01, 0x0e])
    list_key = bytes([0xff])
    fixed_val = 0x4a41279f  # 3845494467

    md5_params = std_md5_enc(std_md5_enc(params.encode('utf-8')))
    md5_post   = std_md5_enc(std_md5_enc(post_data.encode('utf-8')))

    # UA → RC4 → Base64 → MD5
    ua_rc4 = rc4_enc(ua_key, user_agent.encode('utf-8'))
    ua_b64 = base64.b64encode(ua_rc4)
    md5_ua = std_md5_enc(ua_b64)

    # build buffer exactly like Python
    parts = [
        bytes([0x40]),          # literal 64
        ua_key,
        md5_params[14:16],
        md5_post[14:16],
        md5_ua[14:16],
        timestamp.to_bytes(4, 'big'),
        fixed_val.to_bytes(4, 'big'),
    ]
    buffer = b''.join(parts)   # 18 bytes
    checksum = xor_key(buffer)
    buffer += bytes([checksum])  # now 19 bytes

    # final wrapper
    enc = bytes([0x02]) + list_key + rc4_enc(list_key, buffer)

    return custom_b64_encode(enc)

# ──────────────────────────────────────────────────────────────────────
# XGnarly Implementation (without classes/def)
# ──────────────────────────────────────────────────────────────────────

aa = [
    0xFFFFFFFF, 138, 1498001188, 211147047, 253, None, 203, 288, 9,
    1196819126, 3212677781, 135, 263, 193, 58, 18, 244, 2931180889, 240, 173,
    268, 2157053261, 261, 175, 14, 5, 171, 270, 156, 258, 13, 15, 3732962506,
    185, 169, 2, 6, 132, 162, 200, 3, 160, 217618912, 62, 2517678443, 44, 164,
    4, 96, 183, 2903579748, 3863347763, 119, 181, 10, 190, 8, 2654435769, 259,
    104, 230, 128, 2633865432, 225, 1, 257, 143, 179, 16, 600974999, 185100057,
    32, 188, 53, 2718276124, 177, 196, 4294967296, 147, 117, 17, 49, 7, 28, 12,
    266, 216, 11, 0, 45, 166, 247, 1451689750,
]

MASK32 = 0xFFFFFFFF
Ot = [aa[9], aa[69], aa[51], aa[92]]

# Initialize PRNG state
now_ms = int(time.time() * 1000)
kt = [
    aa[44], aa[74], aa[10], aa[62], aa[42], aa[17], aa[2], aa[21], aa[3], 
    aa[70], aa[50], aa[32], aa[0] & now_ms, 
    random.randint(0, 246), random.randint(0, 246), random.randint(0, 246)
]
St = aa[88]

# Helper functions
def u32(x):
    return x & MASK32

def rotl(x, n):
    return u32((x << n) | (x >> (32 - n)))

def quarter(st, a, b, c, d):
    st[a] = u32(st[a] + st[b])
    st[d] = rotl(st[d] ^ st[a], 16)
    st[c] = u32(st[c] + st[d])
    st[b] = rotl(st[b] ^ st[c], 12)
    st[a] = u32(st[a] + st[b])
    st[d] = rotl(st[d] ^ st[a], 8)
    st[c] = u32(st[c] + st[d])
    st[b] = rotl(st[b] ^ st[c], 7)

def chacha_block(state, rounds):
    w = state.copy()
    r = 0
    while r < rounds:
        # column round
        quarter(w, 0, 4, 8, 12)
        quarter(w, 1, 5, 9, 13)
        quarter(w, 2, 6, 10, 14)
        quarter(w, 3, 7, 11, 15)
        r += 1
        if r >= rounds:
            break
        # diagonal round
        quarter(w, 0, 5, 10, 15)
        quarter(w, 1, 6, 11, 12)
        quarter(w, 2, 7, 12, 13)
        quarter(w, 3, 4, 13, 14)
        r += 1
    for i in range(16):
        w[i] = u32(w[i] + state[i])
    return w

def bump_counter(st):
    st[12] = u32(st[12] + 1)

def xgnarly_rand():
    global St
    e = chacha_block(kt, 8)
    t = e[St]
    r = (e[St + 8] & 0xFFFFFFF0) >> 11
    if St == 7:
        bump_counter(kt)
        St = 0
    else:
        St += 1
    return (t + 4294967296 * r) / (2 ** 53)

def num_to_bytes(val):
    if val < 255*255:
        return [(val >> 8) & 0xFF, val & 0xFF]
    else:
        return [(val >> 24) & 0xFF, (val >> 16) & 0xFF, (val >> 8) & 0xFF, val & 0xFF]

def be_int_from_str(s):
    if not s:
        return 0
    buf = s.encode('utf-8')[:4]
    acc = 0
    for b in buf:
        acc = (acc << 8) | b
    return acc & MASK32

def encrypt_chacha(key_words, rounds, data_bytes):
    n_full = len(data_bytes) // 4
    leftover = len(data_bytes) % 4
    words = []
    for i in range(n_full):
        j = i*4
        word = data_bytes[j] | (data_bytes[j+1]<<8) | (data_bytes[j+2]<<16) | (data_bytes[j+3]<<24)
        words.append(word & MASK32)
    if leftover:
        v = 0
        base = 4*n_full
        for c in range(leftover):
            v |= data_bytes[base+c] << (8*c)
        words.append(v & MASK32)
    
    o = 0
    state = key_words.copy()
    while o + 16 < len(words):
        stream = chacha_block(state, rounds)
        bump_counter(state)
        for k in range(16):
            words[o+k] ^= stream[k]
        o += 16
    remain = len(words) - o
    if remain > 0:
        stream = chacha_block(state, rounds)
        for k in range(remain):
            words[o+k] ^= stream[k]
    
    # flatten back to bytes
    result_bytes = bytearray(len(data_bytes))
    for i in range(n_full):
        w = words[i]
        j = 4*i
        result_bytes[j] = w & 0xFF
        result_bytes[j+1] = (w >> 8) & 0xFF
        result_bytes[j+2] = (w >> 16) & 0xFF
        result_bytes[j+3] = (w >> 24) & 0xFF
    if leftover:
        w = words[n_full]
        base = 4*n_full
        for c in range(leftover):
            result_bytes[base+c] = (w >> (8*c)) & 0xFF
    return result_bytes

def ab22(key12_words, rounds, s):
    state = Ot + key12_words
    data = bytearray(s.encode('utf-8'))
    enc = encrypt_chacha(state, rounds, data)
    return enc.decode('latin-1')

def xgnarly_encrypt_auto(query_string, payload, user_agent, envcode=0, version='5.1.1', timestamp_ms=None):
    if timestamp_ms is None:
        timestamp_ms = int(time.time() * 1000)
    
    obj = {}
    obj[1] = 1
    obj[2] = envcode
    obj[3] = hashlib.md5(query_string.encode('utf-8')).hexdigest()
    obj[4] = hashlib.md5(payload.encode('utf-8')).hexdigest()
    obj[5] = hashlib.md5(user_agent.encode('utf-8')).hexdigest()
    obj[6] = timestamp_ms // 1000
    obj[7] = 1508145731
    obj[8] = int((timestamp_ms*1000) % 2147483648)
    obj[9] = version

    if version == '5.1.1':
        obj[10] = '1.0.0.314'
        obj[11] = 1
        v12 = 0
        for i in range(1, 12):
            v = obj[i]
            to_xor = v if isinstance(v, int) else be_int_from_str(v)
            v12 ^= to_xor
        obj[12] = v12 & MASK32
    elif version != '5.1.0':
        raise ValueError(f"Unsupported version: {version}")

    v0 = 0
    for i in range(1, len(obj)+1):
        v = obj[i]
        if isinstance(v, int):
            v0 ^= v
    obj[0] = v0 & MASK32

    payload_bytes = bytearray()
    payload_bytes.append(len(obj))
    for k in sorted(obj.keys()):
        payload_bytes.append(k)
        v = obj[k]
        if isinstance(v, int):
            val_bytes = num_to_bytes(v)
        else:
            val_bytes = list(v.encode('utf-8'))
        payload_bytes.extend(num_to_bytes(len(val_bytes)))
        payload_bytes.extend(val_bytes)
    
    base_str = ''.join(chr(b) for b in payload_bytes)

    key_words = []
    key_bytes = []
    round_accum = 0
    for i in range(12):
        rnd = xgnarly_rand()
        word = int(rnd * 4294967296) & MASK32
        key_words.append(word)
        round_accum = (round_accum + (word & 15)) & 15
        key_bytes.extend([word & 0xFF, (word>>8)&0xFF, (word>>16)&0xFF, (word>>24)&0xFF])
    rounds = round_accum + 5

    enc = ab22(key_words, rounds, base_str)

    insert_pos = 0
    for b in key_bytes:
        insert_pos = (insert_pos + b) % (len(enc)+1)
    for ch in enc:
        insert_pos = (insert_pos + ord(ch)) % (len(enc)+1)

    key_bytes_str = ''.join(chr(b) for b in key_bytes)
    final_str = chr(((1<<6)^(1<<3)^3)&0xFF) + enc[:insert_pos] + key_bytes_str + enc[insert_pos:]

    alphabet = 'u09tbS3UvgDEe6r-ZVMXzLpsAohTn7mdINQlW412GqBjfYiyk8JORCF5/xKHwacP='
    out = []
    full_len = (len(final_str)//3)*3
    for i in range(0, full_len, 3):
        block = (ord(final_str[i])<<16) | (ord(final_str[i+1])<<8) | ord(final_str[i+2])
        out.append(alphabet[(block>>18)&63])
        out.append(alphabet[(block>>12)&63])
        out.append(alphabet[(block>>6)&63])
        out.append(alphabet[block&63])
    return ''.join(out)

# ──────────────────────────────────────────────────────────────────────
# Utils Implementation (without classes/def)
# ──────────────────────────────────────────────────────────────────────

def get_random_int(a, b):
    min_val = min(a, b)
    max_val = max(a, b)
    diff = max_val - min_val + 1
    return min_val + int(random.random() * diff)

def generate_verify_fp():
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    e = len(chars)
    n = int(time.time() * 1000)
    n36 = format(n, 'x')

    r = [''] * 36
    r[8] = r[13] = r[18] = r[23] = '_'
    r[14] = '4'

    for o in range(36):
        if not r[o]:
            i = int(random.random() * e)
            r[o] = chars[(3 & i) | 8 if o == 19 else i]

    return f"verify_{n36}_{''.join(r)}"

def generate_device_id():        
    timestamp = str(int(time.time() * 1000))
    random_part = str(random.randint(0, 999999999)).zfill(9)
    return '7' + timestamp[-9:] + random_part

def generate_ms_token():
    chars = string.ascii_letters + string.digits + "-_"
    return ''.join(random.choice(chars) for _ in range(107))

# ──────────────────────────────────────────────────────────────────────
# Main Sign Function
# ──────────────────────────────────────────────────────────────────────

def sign(params, payload="", user_agent=None):
    if isinstance(params, dict):
        params_dict = params
        params_str = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
    else:
        params_str = params
        if params_str.startswith("http"):
            parsed = urllib.parse.urlparse(params_str)
            query_string = parsed.query
        else:
            query_string = params_str
        params_dict = dict(urllib.parse.parse_qsl(query_string))

    if isinstance(payload, dict):
        payload_str = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in payload.items()])
    else:
        payload_str = payload

    timestamp = (
        int(params_dict.get("ts", 0))
        or int(params_dict.get("time", 0))
        or int(params_dict.get("WebIdLastTime", 0))
        or int(time.time())
    )

    if user_agent is None:
        user_agent = (
            params_dict.get("user_agent")
            or params_dict.get("User-Agent")
            or params_dict.get("browser_version")
            or "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"
        )

    # Generate all values
    verify_fp = generate_verify_fp()
    device_id = generate_device_id()
    iid = generate_device_id()
    ms_token = generate_ms_token()
    x_bogus = xbogus_encrypt(params_str, payload_str, user_agent, timestamp)
    x_gnarly = xgnarly_encrypt_auto(params_str, payload_str, user_agent)
    
    return {
        "verifyFp": verify_fp,
        "device_id": device_id,
        "iid": iid,
        "msToken": ms_token,
        "X-Bogus": x_bogus,
        "X-Gnarly": x_gnarly,
        "timestamp": timestamp,
        "User-Agent": user_agent
    }

params = "https://web-va.tiktok.com/passport/web/region/?aid=1988&app_language=ar&app_name=tiktok_web&browser_language=ar-EG&browser_name=Mozilla&browser_online=true&browser_platform=Linux%20armv81&browser_version=5.0%20%28Linux%3B%20Android%2010%3B%20K%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F137.0.0.0%20Mobile%20Safari%2F537.36&channel=tiktok_web&cookie_enabled=true&data_collection_enabled=false&device_id=7572057782468249119&device_platform=web_mobile&focus_state=true&from_page=&history_len=4&is_fullscreen=false&is_page_visible=true&os=android&priority_region=&referer=https%3A%2F%2Fwww.google.com%2F&region=SA&root_referer=https%3A%2F%2Fwww.google.com%2F&screen_height=851&screen_width=393&tz_name=Asia%2FAden&user_is_login=false&webcast_language"
payload = {"Dev": "Hasneen"}


Signature = sign(params, payload)
print(Signature)