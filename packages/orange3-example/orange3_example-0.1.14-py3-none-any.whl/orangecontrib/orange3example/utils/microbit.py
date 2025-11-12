# -*- coding: utf-8 -*-
import serial
import time
import serial.tools.list_ports
import threading

_connection = None
_text_input_callback = None
_is_listening = False


def list_ports() -> list:
    """Return list of available serial ports"""
    return [port.device for port in serial.tools.list_ports.comports()]


def connect(port: str, baudrate: int = 115200, timeout: float = 1.0) -> str:
    """Attempt to connect to port. Return port name on success."""
    global _connection
    if _connection:
        _connection.close()
    _connection = serial.Serial(port, baudrate=baudrate, timeout=timeout)
    time.sleep(2)  # Wait for connection to stabilize
    return _connection.port


def disconnect():
    """Disconnect"""
    global _connection, _is_listening
    _is_listening = False
    if _connection and _connection.is_open:
        _connection.close()
        _connection = None


def is_connected() -> bool:
    """Return current connection status"""
    global _connection
    return _connection is not None and _connection.is_open


def send_and_receive(message: str, wait_time: float = 2.0) -> str:
    """Send message and receive response"""
    global _connection
    if not _connection or not _connection.is_open:
        raise RuntimeError("Microbit not connected. Call connect(port) first.")

    _connection.reset_input_buffer()  # Clear previous receive buffer
    # Send with CRLF (for compatibility with Microbit/firmware expecting CRLF)
    _connection.write((message + '\r\n').encode('utf-8'))

    time.sleep(wait_time)

    if _connection.in_waiting > 0:
        try:
            response = _connection.readline().decode('utf-8', errors='ignore').strip()
            return response if response else "[No response]"
        except Exception as e:
            return f"[Decoding error: {str(e)}]"
    else:
        return "[Timeout: No response]"


def send_text(text: str) -> bool:
    """Send text to Microbit immediately"""
    global _connection
    if not _connection or not _connection.is_open:
        print("Microbit not connected.")
        return False
    
    try:
        # Clear receive buffer and send with CRLF
        _connection.reset_input_buffer()
        message = text.strip() + '\r\n'
        _connection.write(message.encode('utf-8'))
        _connection.flush()  # Flush buffer immediately
        time.sleep(0.05)  # Short wait for transmission stability
        print(f"Sent: {text}")
        return True
    except Exception as e:
        print(f"Send error: {str(e)}")
        return False


def start_text_listening(callback=None):
    """Start listener to receive text responses from Microbit in real-time"""
    global _connection, _text_input_callback, _is_listening
    
    if not _connection or not _connection.is_open:
        print("Microbit not connected.")
        return False
    
    _text_input_callback = callback
    _is_listening = True
    
    def listen_thread():
        while _is_listening and _connection and _connection.is_open:
            try:
                if _connection.in_waiting > 0:
                    # Read all data with timeout to receive complete response
                    response_parts = []
                    no_data_count = 0
                    max_no_data = 20  # Consider complete if no additional data for 1 second (0.05s * 20)
                    start_time = time.time()
                    max_wait_time = 2.0  # Max wait time 2 seconds
                    
                    while True:
                        current_time = time.time()
                        if current_time - start_time > max_wait_time:
                            break  # Max wait time exceeded
                        
                        if _connection.in_waiting > 0:
                            # Read all available bytes
                            available_bytes = _connection.in_waiting
                            data = _connection.read(available_bytes).decode('utf-8', errors='ignore')
                            if data:
                                response_parts.append(data)
                                no_data_count = 0  # Reset counter if data available
                                start_time = current_time  # Reset time when data arrives
                        else:
                            no_data_count += 1
                            if no_data_count >= max_no_data:
                                break  # No additional data, response complete
                        
                        time.sleep(0.05)  # Short wait
                    
                    if response_parts:
                        # Combine all data and process as one response
                        full_response = "".join(response_parts).strip()
                        # Remove newlines and clean up
                        full_response = full_response.replace('\r', '').replace('\n', ' ')
                        # Merge multiple spaces into one
                        full_response = ' '.join(full_response.split())
                        if full_response and _text_input_callback:
                            _text_input_callback(full_response)
                time.sleep(0.1)  # Reduce CPU usage
            except Exception as e:
                print(f"Listening error: {str(e)}")
                break
    
    # Start listening in separate thread
    listener = threading.Thread(target=listen_thread, daemon=True)
    listener.start()
    print("Microbit response listening started")
    return True


def stop_text_listening():
    """Stop text response listening"""
    global _is_listening
    _is_listening = False
    print("Microbit response listening stopped")


def send_text_with_response(text: str, wait_time: float = 1.0) -> str:
    """Send text and wait for response"""
    if send_text(text):
        time.sleep(wait_time)
        if _connection and _connection.in_waiting > 0:
            try:
                response = _connection.readline().decode('utf-8', errors='ignore').strip()
                return response if response else "[No response]"
            except Exception as e:
                return f"[Response read error: {str(e)}]"
        else:
            return "[No response]"
    return "[Send failed]"
