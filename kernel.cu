#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>
#include <math.h>
#include <time.h>   // 新增：用于获取时间
#include <string.h> // 新增：用于字符串处理

// ---------------------------------------------------------
// 1. 数据结构定义
// 必须与 Python erjinzhi.py 的打包格式(10个float)完全一致
// ---------------------------------------------------------
struct PitchPhysics {
    int type;            // 0=FF, 1=SI, 2=SL, 3=CU, 4=CH
    float speed;
    float spin;
    float vx0, vy0, vz0;
    float ax, ay, az;
    float px, pz;        // 进垒坐标
    int is_hit_actual;
};

// 战术分析结果
struct SniperResult {
    int predict_hit;    // 0或1
    float threat_score; // 威胁程度 (0-100)
    int reason_code;    // 1:失速, 2:呆滞, 3:死转, 4:平移
};

// ---------------------------------------------------------
// 2. CUDA Kernel: 战术指挥中心 V3.0
// ---------------------------------------------------------
__global__ void physics_sniper_v3(PitchPhysics* data, SniperResult* results, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n) return;

    PitchPhysics p = data[idx];
    const float G = -32.174f;
    float lift = p.az - G; 
    
    int hit = 0;
    float score = 0.0f;
    int reason = 0; 

    // --- 核心战术建模 ---
    // 策略 A: 直球系
    if (p.type == 0 || p.type == 1) {
        if (p.speed < 93.0f) { score += 40.0f; reason = 1; }
        if (lift < 11.0f) { 
            score += 35.0f; 
            if (reason == 1) score += 15.0f; else reason = 2; 
        }
    } 
    // 策略 B: 变化球系
    else if (p.type == 2 || p.type == 3) {
        if (p.spin < 2100.0f) { score += 45.0f; reason = 3; }
        if (fabsf(p.ax) < 3.0f && p.type == 2) { score += 40.0f; reason = 4; }
    }
    // 策略 C: 变速球
    else if (p.type == 4) {
        if (p.speed > 88.0f) { score += 50.0f; reason = 1; }
    }

    if (score >= 60.0f) hit = 1;
    if (score > 100.0f) score = 100.0f;

    results[idx].predict_hit = hit;
    results[idx].threat_score = score;
    results[idx].reason_code = reason;
}

// ---------------------------------------------------------
// 新增函数：写日志
// ---------------------------------------------------------
void write_log(int count) {
    FILE* log_file = fopen("cuda_activity.log", "a"); // 使用 "a" (append) 模式追加日志
    if (log_file) {
        time_t now;
        time(&now);
        char* time_str = ctime(&now);
        // 去掉时间字符串末尾的换行符
        time_str[strcspn(time_str, "\n")] = 0;
        
        fprintf(log_file, "[%s] GPU KERNEL EXECUTED | Vectors Processed: %d | Status: SUCCESS\n", time_str, count);
        fclose(log_file);
        printf(">> Log written to cuda_activity.log\n");
    } else {
        printf(">> Failed to write log file!\n");
    }
}

// ---------------------------------------------------------
// 3. Host 主程序
// ---------------------------------------------------------
int main() {
    const char* input_file = "mlb_physics_full.bin";
    const char* output_file = "sniper_results.bin";

    printf("=== COMMANDER V3.0: TACTICAL ENGINE START ===\n");

    // 1. 读取输入
    FILE* f = fopen(input_file, "rb");
    if (!f) { 
        printf("Error: No input file (%s).\n", input_file); 
        // 即使失败也写一个错误日志
        FILE* log = fopen("cuda_activity.log", "a");
        if(log) { fprintf(log, "ERROR: Input file not found.\n"); fclose(log); }
        return 1; 
    }
    
    int n;
    fread(&n, sizeof(int), 1, f);
    printf("Loading %d pitches into VRAM...\n", n);

    size_t input_size = n * sizeof(PitchPhysics);
    size_t output_size = n * sizeof(SniperResult);

    PitchPhysics* h_data = (PitchPhysics*)malloc(input_size);
    fread(h_data, input_size, 1, f);
    fclose(f);

    // 2. GPU 内存分配与拷贝
    PitchPhysics* d_data;
    SniperResult* d_results;
    cudaMalloc(&d_data, input_size);
    cudaMalloc(&d_results, output_size);
    
    cudaMemcpy(d_data, h_data, input_size, cudaMemcpyHostToDevice);

    // 3. 发射核函数
    int threads = 256;
    int blocks = (n + threads - 1) / threads;
    
    physics_sniper_v3<<<blocks, threads>>>(d_data, d_results, n);
    
    // 检查是否有 CUDA 错误
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        printf("CUDA Error: %s\n", cudaGetErrorString(err));
        return 1;
    }
    
    cudaDeviceSynchronize();

    // 4. 取回结果
    SniperResult* h_results = (SniperResult*)malloc(output_size);
    cudaMemcpy(h_results, d_results, output_size, cudaMemcpyDeviceToHost);

    // 5. 写入结果文件
    FILE* fw = fopen(output_file, "wb");
    fwrite(&n, sizeof(int), 1, fw); 
    fwrite(h_results, output_size, 1, fw);
    fclose(fw);

    printf("Analysis Complete. Tactical data written to %s\n", output_file);
    
    // 【关键步骤】写日志证明我来过
    write_log(n);

    // 清理
    free(h_data); free(h_results);
    cudaFree(d_data); cudaFree(d_results);
    return 0;
}