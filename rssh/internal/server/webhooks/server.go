package webhooks

import (
	"crypto/tls"
	"encoding/json"
	"github.com/NHAS/reverse_ssh/internal/server/data"
	"github.com/NHAS/reverse_ssh/internal/server/observers"
	"github.com/valyala/fasthttp"
	"log"
)

var (
	client = fasthttp.Client{
		NoDefaultUserAgentHeader: true,
		TLSConfig:                &tls.Config{InsecureSkipVerify: true, MaxVersion: tls.VersionTLS13, MinVersion: tls.VersionTLS10},
		MaxConnsPerHost:          5,
		RetryIfErr: func(request *fasthttp.Request, attempts int, err error) (resetTimeout bool, retry bool) {
			if err != nil {
				return false, true
			}
			return false, false
		},
	}
)

func StartWebhooks() {

	messages := make(chan observers.ClientState)

	observers.ConnectionState.Register(func(message observers.ClientState) {
		messages <- message
	})

	go func() {
		for msg := range messages {

			//go func(msg observers.ClientState) {
			//
			//	fullBytes, err := msg.Json()
			//	if err != nil {
			//		log.Println("Bad webhook message: ", err)
			//		return
			//	}
			//
			//	wrapper := struct {
			//		Full string
			//		Text string `json:"text"`
			//	}{
			//		Full: string(fullBytes),
			//		Text: msg.Summary(),
			//	}
			//
			//	webhookMessage, _ := json.Marshal(wrapper)
			//
			//	recipients, err := data.GetAllWebhooks()
			//	if err != nil {
			//		log.Println("error fetching webhooks: ", err)
			//		return
			//	}
			//
			//	for _, webhook := range recipients {
			//
			//		//tr := &http.Transport{
			//		//	TLSClientConfig: &tls.Config{InsecureSkipVerify: webhook.CheckTLS},
			//		//}
			//		//
			//		//client := http.Client{
			//		//	Timeout:   30 * time.Second,
			//		//	Transport: tr,
			//		//}
			//		//buff := bytes.NewBuffer(webhookMessage)
			//		req := fasthttp.AcquireRequest()
			//		resp := fasthttp.AcquireResponse()
			//		req.SetRequestURI(webhook.URL)
			//		req.Header.SetMethod(fasthttp.MethodPost)
			//		req.Header.SetContentType("application/json")
			//		req.SetBody(webhookMessage)
			//		if err = client.Do(req, resp); err != nil {
			//			log.Printf("Error sending webhook '%s': %s\n", webhook.URL, err)
			//		}
			//
			//		//_, err := client.Post(webhook.URL, "application/json", buff)
			//		//if err != nil {
			//		//	log.Printf("Error sending webhook '%s': %s\n", webhook.URL, err)
			//		//}
			//	}
			//}(msg)

			fullBytes, err := msg.Json()
			if err != nil {
				log.Println("Bad webhook message: ", err)
				return
			}

			wrapper := struct {
				Full string
				Text string `json:"text"`
			}{
				Full: string(fullBytes),
				Text: msg.Summary(),
			}

			webhookMessage, _ := json.Marshal(wrapper)

			recipients, err := data.GetAllWebhooks()
			if err != nil {
				log.Println("error fetching webhooks: ", err)
				return
			}

			for _, webhook := range recipients {

				//tr := &http.Transport{
				//	TLSClientConfig: &tls.Config{InsecureSkipVerify: webhook.CheckTLS},
				//}
				//
				//client := http.Client{
				//	Timeout:   30 * time.Second,
				//	Transport: tr,
				//}
				//buff := bytes.NewBuffer(webhookMessage)
				req := fasthttp.AcquireRequest()
				resp := fasthttp.AcquireResponse()
				req.SetRequestURI(webhook.URL)
				req.Header.SetMethod(fasthttp.MethodPost)
				req.Header.SetContentType("application/json")
				req.SetBody(webhookMessage)
				if err = client.Do(req, resp); err != nil {
					log.Printf("Error sending webhook '%s': %s\n", webhook.URL, err)
				}

				//_, err := client.Post(webhook.URL, "application/json", buff)
				//if err != nil {
				//	log.Printf("Error sending webhook '%s': %s\n", webhook.URL, err)
				//}
			}

		}
	}()
}
