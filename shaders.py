

vertexShader = '''
#version 450 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec2 texCoords;
layout (location = 2) in vec3 normals;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

out vec2 uvs;
out vec3 outPosition;
out vec3 outNormals;

void main() {
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1);
    uvs = texCoords;
    outNormals = (modelMatrix * vec4(normals, 0)).xyz;
    outPosition = position;
    outNormals = normalize(outNormals);
}

'''

fragmentShader = '''
#version 450 core

layout (binding = 0) uniform sampler2D tex;

in vec2 uvs;
in vec3 outPosition;
in vec3 outNormals;

out vec4 fragColor;

void main() {
    fragColor = texture(tex, uvs);
}

'''

fragmentShaderWithLight = '''
#version 450 core

layout (binding = 0) uniform sampler2D tex;

uniform vec3 directionalLight;

in vec2 uvs;
in vec3 outNormals;

out vec4 fragColor;

void main() {
    float intensity = dot(outNormals, -directionalLight);
    intensity = min(1, intensity);
    intensity = max(0, intensity);
    fragColor = texture(tex, uvs) * intensity;
}

'''

###############################################################################################

distortionVertex = '''
#version 450 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec2 texCoords;
layout (location = 2) in vec3 normals;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float time;

out vec2 uvs;
out vec3 outPosition;
out vec3 outNormals;
out vec3 originalPosition;

float noise(vec3 x, vec3 y) {
    vec3 p = floor(x);
    vec3 f = fract(x);
    float n = p.x + p.y * 157 + 113 * p.z;

    if (sin(time) < 0) f = f * f * (3 - 2 *f);
    else f = f * f * f + sin(time) / 8;
    
    vec4 v1 = fract(753 * sin(n + vec4(0, 1, 157, 158)));
    vec4 v2 = fract(753 * cos(n + vec4(113, 114, 270, 271)));
    vec4 v3 = mix(v1, v2, f.z);
    vec2 v4 = mix(v3.xy, v3.zw, f.y);
    return mix(v4.x, v4.y, f.x);
}

void main() {
    float b = 5 * noise(0.1 * position, vec3( 1.0 ));
    float displacement = sin(time) * 0.1 + b;
    vec3 distortedPosition = position + normals * displacement;
    
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(distortedPosition, 1);
    uvs = texCoords;
    outPosition = (modelMatrix * vec4(position, 1) * vec4(distortedPosition, 1)).xyz;
    outNormals = (modelMatrix * vec4(normals, 0)).xyz;
    outNormals = normalize(outNormals);
    originalPosition = position;
}

'''

colorFulFragment = '''
#version 450 core

layout (binding = 0) uniform sampler2D tex;

uniform float time;
uniform vec3 directionalLight;

in vec2 uvs;
in vec3 outNormals;
in vec3 outPosition;
in vec3 originalPosition;

out vec4 fragColor;

void main() {
    float inkStrength = smoothstep(0.5, 0.45, length(uvs - 0.5)) * 0.5 + sin(time * 5.0) / 2;
    float ink = max(0.0, inkStrength - length(uvs));
    ink = max(ink, inkStrength - cos(time * 5));
    
    vec3 viewDir = normalize(-outPosition);
    
    vec3 reflection = reflect(viewDir, outNormals).xyz;
    vec3 baseColor = texture(tex, uvs).xyz;
    vec3 finalColor = mix(baseColor, reflection, ink);

    fragColor = vec4(finalColor, 1);
}
'''

clockVertex = '''
#version 450 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec2 texCoords;
layout (location = 2) in vec3 normals;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;

out vec2 uvs;
out vec3 outPosition;
out vec3 outNormals;
out float angle;

vec2 Break(vec2 vector, float angle)
{
  vec2 result;
  result.x = cos(angle) * vector.x - sin(angle) * vector.y;
  result.y = sin(angle) * vector.x + cos(angle) * vector.y;
  return result;
}

void main() {
    mat4 modelM = modelMatrix;
    float springFactor = 0.9;
    float new = cos(2 * time) * springFactor;
    modelM[2][1] = modelM[2][1] + new;
    
    vec3 pos = position;
    angle = 2 * pos.y * tan(time);
    pos.xz = Break(pos.xz, angle);

    gl_Position = projectionMatrix * viewMatrix * modelM * vec4(pos, 1);
    
    outNormals = (modelM * vec4(normals, 0)).xyz;
    outNormals = normalize(outNormals);
    outPosition = pos;
    uvs = texCoords;
}
'''

theMatrixFragment = '''
#version 450 core

layout (binding = 0) uniform sampler2D tex;

uniform float time;

in vec2 uvs;
in vec3 outPosition;
in vec3 outNormals;
in float angle;

out vec4 fragColor;

void main() {
    vec3 baseColor = texture(tex, uvs).xyz;
    
    if (angle > 0 && mod(time * 1000, 4) > 0 || mod(time * 1000, 4) < 0) {
        float randomValue = fract(sin(dot(uvs, vec2(12,78)) * 65646 + time));

        float rayThreshold = 0.5;

        if (randomValue > rayThreshold) {
            vec3 rayColor = vec3(0,1,0);
            baseColor += rayColor;
        }
    }

    fragColor = vec4(baseColor, 1);
}
'''

powerFragment = '''
// Fuente: https://shadered.org/view?s=6Gny24_ojD
#version 450 core
precision highp float;

layout (binding = 0) uniform sampler2D tex;

uniform float time;
uniform vec2 resolution;

in vec2 uvs;
in vec3 outPosition;
in vec3 outNormals;

out vec4 fragColor;


void main(void) {    
    vec4 col1 = vec4(0.886, 0.325, 0.325, 1.0);
    vec4 col2 = vec4(0.804, 0.200, 0.200, 1.0);
    vec4 col3 = vec4(0.690, 0.145, 0.145, 1.0);
    vec4 col4 = vec4(0.514, 0.059, 0.059, 1.0);
    
    vec3 displace = texture(tex, vec2(uvs.x, (uvs.y + time ) * 0.05)).xyz;
	displace += 0.5;
	displace.x -= 1.0;
	displace.y -= 1.0;
	displace.y *= 0.5;
    
    vec2 uv_tmp = uvs;
	uv_tmp.y *= 0.5;
	uv_tmp.y += time;
    vec4 color = texture(tex, uv_tmp + displace.xy);
    
    vec4 noise = floor(color * 15) / 5;
    vec4 dark   = mix(col1, col2, uvs.y);
    vec4 bright = mix(col3, col4, uvs.y);
    color = mix(dark, bright, noise);
    
    float inv_uv = 1 - uvs.y;
    color.xyz -= 0.45 * pow(uvs.y, 8);
    color.a -= 0.2 * pow(uvs.y, 8);
    color += pow(inv_uv, 8);
    
    color.a -= 0.2;

    fragColor = vec4(color);
}
'''

shininessFragment = '''
// Fuente: http://shdr.bkcore.com/#1/jVbbbuM2EP0Vwn2hElmRHXeBzaIvabtFkdYNsEFe6sJgpJHNhUSqJOWVs8i/d0jdSGXT1oAlmnM/c4b010Uus6YCYfTi5s/Fd9AaEJpLQX75bf/Hz5/22jCRM5Xvc1D8xAw/gSY3BAR7KmEndqJWkHFnceSHY02KUjLzYScawQupqu43MbwCb/ME2Zoo0LJsDJqi5MTUmYuDlVyT4l5q/k3BFq1ZOd+Wnv5OVMxck0xi4gesa18oVgHtFLdx967jLoXmRKKd+LoTBD9XV+QAhkB+ACs1UmkiC2KOQGreQkmM4ujTlm3VnaO8XpEfSP4xbympSfQhEK070XkmWpO8OU1mNoeZcDIchGOGCNkJXE4lF8AU0WdtoArj1qBqdJEpqTW1GzHZzpNbhUqIjK0lUHqwafTeLlzSSUsuR1u3tU5a3+T2tcn5tck5KCmTQhvVZIYwojNWwpLb9iLWhrjm9aodk1BWsRbD4AKUBv23MpTgFhYqDX2IH6LYrW7j24hEY0UKTKMEseSgWNlF7yjGlKd1h9KLZVHHE1Bo9bQXjnYzEj32JDLQZlKqvN++9yjlNipmcbZLmklNl/dJe7FJkxRxsWOB4VdpmmDWqyR1jyFlR+SH263t0pzOmMQSExhiz8vsEubPqGkdXLgkwtoUr6hbZLKUKu7hxXlXZvgBIh+WmYRiqMtZdREwtSlUP51dKk4JzhBoLMfJTtrzc6fY+cdsUFNXUpojErqmfSIuBcSELF1TO1exdRx15n3BWcmqmqKXmKQDjFi2Tdu9sESv+jV5wvER90cpDj9xRYO+lniOGdwdSne/fxUjKndsXI3w3OkRwCMXOJlaB2jpAIYhgofU6Q2cPBURqGw9yTGQnC61j2zOi6LRtg93DCl3lyMeQ0mOGC11iDl4Y6Ij31jXkKEl1oeqtfxCZ+rHCHk7lex3xMJM++CxczTxT/IcA3NBA5C2/8Gmx3/FyFrP5hU7ijNyKPcfFTv8aOcEaRdP14XnG5nD0cEwFNTOYpp8j980spRa28d7bzxHFqFVSKaeR85F/x2GO02u7eNd/9isPW/9IA5HBUZ7H1v9NFlZJtsY7vh1C3eCTpWNdhvqnFzacsZkXxbx4q1rmhm81Z4aA/3FOF2kM4kYbt7hDnenU7f7O0PVNpRtSCVzKB85fPm2uFbyM96yGGyU/5+7/s3/BuGfgNcU6/0FHPLTR4yFx7jRnaXV5Nm1amN3cH9WIXpwLRjUPbYUoTd7+g0d9CUzSNzMadfBv+KFi7a46d76SjfPTAjY234mn/Xi5R8=
#version 450 core

layout (binding = 0) uniform sampler2D tex;

uniform float time;
uniform vec2 resolution;

in vec2 uvs;
in vec3 outPosition;
in vec3 outNormals;

out vec4 fragColor;

mat3 cotangentCalc()
{
    vec3 point = normalize(outPosition);
    vec3 dx = dFdx(point);
    vec3 dy = dFdy(point);
    vec2 dxuv = dFdx(uvs);
    vec2 dyuv = dFdy(uvs);
 
    vec3 dp2perp = cross(dy, outNormals);
    vec3 dp1perp = cross(outNormals, dx);
    vec3 T = dp2perp * dxuv.x + dp1perp * dyuv.x;
    vec3 B = dp2perp * dxuv.y + dp1perp * dyuv.y;
 
    float invmax = inversesqrt(max(dot(T,T), dot(B,B)));
    return mat3(T * invmax, B * invmax, outNormals);
}

vec3 perturbNormal()
{
    vec3 map = vec3(1.0, cos(-outPosition.x * 40 + time * 10 ), 1);
    mat3 cotangent = cotangentCalc();
    return normalize(cotangent * map);
}

vec3 rimEffect(vec3 color, float start, float end, float coef)
{
    vec3 normal = normalize(outNormals);
    vec3 eye = normalize(-outPosition.xyz);
    float rim = smoothstep(start, end, 1 - dot(normal, eye));
    return clamp(rim, 0, 1) * coef * color;
}

vec2 phongColor(vec3 N, vec3 lightDir, float lightInt, float Ks, float shininess)
{
    vec3 s = normalize(lightDir);
    vec3 v = normalize(-outPosition);
    vec3 n = normalize(N);
    vec3 h = normalize(v + s);
    float diffuse = lightInt * max(0, dot(n, s));
    float spec =  Ks * pow(max(0, dot(n,h)), shininess);
    return vec2(diffuse, spec);
}

void main()
{
    vec3 newNormal = perturbNormal();
    vec3 rimLight = rimEffect(vec3(0.5,1,1), 0.5, 0.9, 0.5);
    
    vec2 phongColor = phongColor(newNormal, vec3(sin(time), cos(time), sin(time)*cos(time)), 1, 0.6, 10);
    
    vec3 color = vec3(0,0,0) * phongColor.x + phongColor.y;
    fragColor = vec4(color + rimLight, 1);
}
'''