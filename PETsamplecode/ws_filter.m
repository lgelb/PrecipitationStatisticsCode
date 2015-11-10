% This script loads hourly windspeed data and filters it spectrally using
% a fast fourier transformation and a weighting function to pull out an
% overall trend.

data = load('wind_speed.dat');
tm = data(:,1);     % time vector
s = data(:,2);      % wind speed signal
npts = length(tm);
dt = .001;

for j = 1:npts
    frq(j) = (j-1)/(npts*dt);       % this loop creates a frequency vector for plotting in the frequency domain
end

hk = fft(s);  % fast fouier transformation of wind speed sig

figure(1);
clf;
plot(tm,s,'b','linewidth',2);	% plot signal in time domain
xlim([min(tm) max(tm)]);
ylabel('Amplitude');
xlabel('Time (s)');
title('Graph of test signal','fontsize',18);

figure(2);
clf;	
plot(frq,abs(hk),'g','linewidth',2);		% plot fft in frequency domain
xlabel('frequency');
ylabel('Amplitude of FFT');
title('Amplitude of FFT','fontsize',18);
pause;

df = 1/(npts*dt);
f = 5;                        % picked cutoff frequency (from inspection)
Jc = floor((f/df)+1);				% define cutoff frequency
W = zeros(npts,1);				% initialize weighting vector
W(1) = 1;
for J = 2:Jc
	W(J) = 1;		
	K = npts+2-J;				% fill up weighting vector
	W(K) = 1;	
end
	
windowed_signal = hk.*W;			% multiply weight by original signal

figure(3);
clf;
plot(frq,abs(windowed_signal),'m','linewidth',2);	% plot windowed frequency in freq domain
xlabel('frequency');
ylabel('amplitude');
title('Windowed Frequency','fontsize',18);

wind_sig_tm = ifft(windowed_signal);		% inverse fft to go back to time domain

figure(4);
clf;
plot(tm,wind_sig_tm,'k','linewidth',2);		% plot windowed signal in time domain
xlabel('time (s)');
ylabel('amplitude');
title('Windowed signal, time domain','fontsize',18);
xlim([min(tm) max(tm)]);