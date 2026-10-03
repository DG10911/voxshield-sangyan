// Package voxshield is a thin Go client over the VoxShield REST API.
//
//	c := voxshield.New("http://localhost:8000")
//	res, _ := c.Analyze("call.wav")
//	risk, _ := c.RiskScore(map[string]float64{"neural:xls-r": 0.92}, nil)
//
// Standard library only. Mirrors backend/app.py endpoints.
package voxshield

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strconv"
	"time"
)

type Client struct {
	Base string
	HTTP *http.Client
}

func New(base string) *Client {
	return &Client{Base: base, HTTP: &http.Client{Timeout: 60 * time.Second}}
}

type JSON = map[string]interface{}

// ---- core ----
func (c *Client) Health() (JSON, error)            { return c.get("/api/health") }
func (c *Client) Analyze(path string) (JSON, error) { return c.upload("/api/analyze", map[string]string{"file": path}) }
func (c *Client) StreamAnalyze(path string, threshold float64) (JSON, error) {
	return c.upload("/api/stream-analyze?threshold="+strconv.FormatFloat(threshold, 'f', 2, 64), map[string]string{"file": path})
}
func (c *Client) SpeakerVerify(reference, probe string) (JSON, error) {
	return c.upload("/api/speaker/verify", map[string]string{"reference": reference, "probe": probe})
}

// ---- intelligence / risk ----
func (c *Client) RiskScore(perModel map[string]float64, context JSON) (JSON, error) {
	if context == nil {
		context = JSON{}
	}
	return c.post("/api/risk/score", JSON{"per_model": perModel, "context": context})
}
func (c *Client) Threats(n int) (JSON, error) { return c.get("/api/threats?n=" + strconv.Itoa(n)) }
func (c *Client) ThreatSearch(language string, minEer float64) (JSON, error) {
	q := url.Values{"min_eer": {strconv.FormatFloat(minEer, 'f', 2, 64)}}
	if language != "" {
		q.Set("language", language)
	}
	return c.get("/api/threat/search?" + q.Encode())
}
func (c *Client) Intel(q url.Values) (JSON, error) { return c.get("/api/intel?" + q.Encode()) }

// ---- product surfaces ----
func (c *Client) GatewayDecide(voxscore, context JSON) (JSON, error) {
	if context == nil {
		context = JSON{}
	}
	return c.post("/api/gateway/decide", JSON{"voxscore": voxscore, "context": context})
}
func (c *Client) ConsumerCheck(voxscore JSON) (JSON, error) {
	return c.post("/api/consumer/check", JSON{"voxscore": voxscore})
}
func (c *Client) DeploymentProfile(surface string) (JSON, error) {
	return c.get("/api/deployment/profile?surface=" + surface)
}
func (c *Client) Warroom() (JSON, error) { return c.get("/api/warroom") }

// ---- transport ----
func (c *Client) get(path string) (JSON, error) {
	r, err := c.HTTP.Get(c.Base + path)
	if err != nil {
		return nil, err
	}
	return decode(r)
}

func (c *Client) post(path string, payload JSON) (JSON, error) {
	b, _ := json.Marshal(payload)
	r, err := c.HTTP.Post(c.Base+path, "application/json", bytes.NewReader(b))
	if err != nil {
		return nil, err
	}
	return decode(r)
}

func (c *Client) upload(path string, files map[string]string) (JSON, error) {
	var buf bytes.Buffer
	w := multipart.NewWriter(&buf)
	for field, fp := range files {
		f, err := os.Open(fp)
		if err != nil {
			return nil, err
		}
		part, _ := w.CreateFormFile(field, filepath.Base(fp))
		io.Copy(part, f)
		f.Close()
	}
	w.Close()
	r, err := c.HTTP.Post(c.Base+path, w.FormDataContentType(), &buf)
	if err != nil {
		return nil, err
	}
	return decode(r)
}

func decode(r *http.Response) (JSON, error) {
	defer r.Body.Close()
	body, _ := io.ReadAll(r.Body)
	if r.StatusCode >= 400 {
		return nil, fmt.Errorf("voxshield %d: %s", r.StatusCode, string(body))
	}
	var out JSON
	return out, json.Unmarshal(body, &out)
}
