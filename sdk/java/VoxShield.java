package com.voxshield;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.Map;

/**
 * VoxShield Java SDK — thin client over the REST API (java.net.http, JDK 11+).
 *
 *   VoxShield vs = new VoxShield("http://localhost:8000");
 *   String verdict = vs.analyze("call.wav");
 *   String risk = vs.riskScore("{\"per_model\":{\"neural:xls-r\":0.92}}");
 *
 * Returns raw JSON strings (bring your own JSON lib to parse). No third-party deps.
 * Mirrors backend/app.py endpoints.
 */
public class VoxShield {
    private final String base;
    private final HttpClient http;

    public VoxShield(String baseUrl) {
        this.base = baseUrl.replaceAll("/+$", "");
        this.http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(60)).build();
    }

    // ---- core ----
    public String health() throws IOException, InterruptedException { return get("/api/health"); }
    public String analyze(String wavPath) throws IOException, InterruptedException {
        return upload("/api/analyze", Map.of("file", wavPath));
    }
    public String streamAnalyze(String wavPath, double threshold) throws IOException, InterruptedException {
        return upload("/api/stream-analyze?threshold=" + threshold, Map.of("file", wavPath));
    }
    public String speakerVerify(String reference, String probe) throws IOException, InterruptedException {
        return upload("/api/speaker/verify", Map.of("reference", reference, "probe", probe));
    }

    // ---- intelligence / risk (payload = raw JSON string) ----
    public String riskScore(String jsonBody) throws IOException, InterruptedException { return post("/api/risk/score", jsonBody); }
    public String threats(int n) throws IOException, InterruptedException { return get("/api/threats?n=" + n); }
    public String threatSearch(String query) throws IOException, InterruptedException { return get("/api/threat/search?" + query); }
    public String intel(String query) throws IOException, InterruptedException { return get("/api/intel?" + query); }

    // ---- product surfaces ----
    public String gatewayDecide(String jsonBody) throws IOException, InterruptedException { return post("/api/gateway/decide", jsonBody); }
    public String consumerCheck(String jsonBody) throws IOException, InterruptedException { return post("/api/consumer/check", jsonBody); }
    public String deploymentProfile(String surface) throws IOException, InterruptedException { return get("/api/deployment/profile?surface=" + surface); }
    public String warroom() throws IOException, InterruptedException { return get("/api/warroom"); }

    // ---- transport ----
    private String get(String path) throws IOException, InterruptedException {
        HttpRequest req = HttpRequest.newBuilder(URI.create(base + path)).GET().build();
        return send(req);
    }

    private String post(String path, String jsonBody) throws IOException, InterruptedException {
        HttpRequest req = HttpRequest.newBuilder(URI.create(base + path))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody)).build();
        return send(req);
    }

    private String upload(String path, Map<String, String> files) throws IOException, InterruptedException {
        String boundary = "----voxshield" + System.currentTimeMillis();
        var baos = new java.io.ByteArrayOutputStream();
        for (var e : files.entrySet()) {
            byte[] data = Files.readAllBytes(Path.of(e.getValue()));
            String name = Path.of(e.getValue()).getFileName().toString();
            baos.write(("--" + boundary + "\r\nContent-Disposition: form-data; name=\"" + e.getKey()
                    + "\"; filename=\"" + name + "\"\r\nContent-Type: application/octet-stream\r\n\r\n").getBytes());
            baos.write(data);
            baos.write("\r\n".getBytes());
        }
        baos.write(("--" + boundary + "--\r\n").getBytes());
        HttpRequest req = HttpRequest.newBuilder(URI.create(base + path))
                .header("Content-Type", "multipart/form-data; boundary=" + boundary)
                .POST(HttpRequest.BodyPublishers.ofByteArray(baos.toByteArray())).build();
        return send(req);
    }

    private String send(HttpRequest req) throws IOException, InterruptedException {
        HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() >= 400) {
            throw new IOException("VoxShield " + resp.statusCode() + ": " + resp.body());
        }
        return resp.body();
    }
}
