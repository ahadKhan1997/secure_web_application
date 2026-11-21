import React, { useState } from 'react';
import api from './services/api';
import { Card } from 'primereact/card';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Dropdown } from 'primereact/dropdown';

import 'primereact/resources/themes/lara-light-indigo/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [role, setRole] = useState('subscriber');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // SIM Swap Form State
  const [msisdn, setMsisdn] = useState('');
  const [iccid, setIccid] = useState('');
  const [reason, setReason] = useState('');
  const [swapType, setSwapType] = useState('physical_to_esim');
  const [requests, setRequests] = useState([]);

  const swapOptions = [
    { label: 'Physical SIM to eSIM', value: 'physical_to_esim' },
    { label: 'eSIM Replacement', value: 'esim_replacement' },
    { label: 'Device Change', value: 'device_change' }
  ];

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const res = await api.post('/auth/login', formData);
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('csrf_token', res.data.csrf_token);
      setRole(res.data.role);
      setIsLoggedIn(true);
      fetchRequests(res.data.role);
    } catch (err) {
      alert('Login Failed: ' + (err.response?.data?.detail || 'Invalid credentials'));
    }
  };

  const fetchRequests = async (userRole) => {
    try {
      const endpoint = userRole === 'admin' ? '/admin/swap-requests' : '/swap-requests/me';
      const res = await api.get(endpoint);
      setRequests(res.data);
    } catch (err) {
      console.error('Fetch requests error:', err);
    }
  };

  const handleSubmitSwap = async (e) => {
    e.preventDefault();
    try {
      await api.post('/swap-requests', {
        target_msisdn: msisdn,
        current_iccid: iccid,
        reason: reason,
        swap_type: swapType
      });
      alert('SIM Swap request submitted successfully!');
      fetchRequests(role);
    } catch (err) {
      alert('Submission failed: ' + (err.response?.data?.detail || 'Forbidden/Error'));
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="flex justify-content-center align-items-center min-h-screen surface-ground">
        <Card title="Telecom eSIM Portal Login" style={{ width: '400px' }}>
          <form onSubmit={handleLogin} className="flex flex-column gap-3">
            <span className="p-float-label">
              <InputText id="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full" />
              <label htmlFor="email">Email Address</label>
            </span>
            <span className="p-float-label">
              <InputText id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full" />
              <label htmlFor="password">Password</label>
            </span>
            <Button label="Login" icon="pi pi-sign-in" type="submit" className="w-full" />
          </form>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-4 surface-ground min-h-screen">
      <div className="flex justify-content-between align-items-center mb-4">
      <a href="https://telecom-support.example.com" target="_blank" rel="noreferrer">Support Portal</a>
        <h2>Telecom Dashboard ({role.toUpperCase()})</h2>
        <Button label="Logout" icon="pi pi-power-off" className="p-button-danger" onClick={() => setIsLoggedIn(false)} />
      </div>

      {role === 'subscriber' && (
        <Card title="Request SIM Swap / eSIM Activation" className="mb-4">
          <form onSubmit={handleSubmitSwap} className="grid p-fluid">
            <div className="col-12 md:col-4">
              <InputText placeholder="Target Phone Number (MSISDN)" value={msisdn} onChange={(e) => setMsisdn(e.target.value)} />
            </div>
            <div className="col-12 md:col-4">
              <InputText placeholder="Current SIM ICCID" value={iccid} onChange={(e) => setIccid(e.target.value)} />
            </div>
            <div className="col-12 md:col-4">
              <Dropdown value={swapType} options={swapOptions} onChange={(e) => setSwapType(e.value)} placeholder="Select Swap Type" />
            </div>
            <div className="col-12">
              <InputText placeholder="Reason for Swap" value={reason} onChange={(e) => setReason(e.target.value)} />
            </div>
            <div className="col-12">
              <Button label="Submit Request" icon="pi pi-send" type="submit" />
            </div>
          </form>
        </Card>
      )}

      <Card title={role === 'admin' ? 'Global SIM Swap Request Queue' : 'My SIM Swap History'}>
        <DataTable value={requests} responsiveLayout="scroll">
          <Column field="id" header="Request ID" />
          <Column field="user_id" header="User ID" />
          <Column field="target_msisdn" header="MSISDN" />
          <Column field="current_iccid" header="ICCID" />
          <Column field="swap_type" header="Type" />
          <Column field="status" header="Status" />
        </DataTable>
      </Card>
    </div>
  );
}

export default App;