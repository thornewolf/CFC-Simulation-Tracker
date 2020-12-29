
close all;clc;clear;

fprintf('Choose the first P00# that you wish to start from.\n')
[file,path]=uigetfile('*.*');
original_file_name = file;

file_count = input('How many consecutive incremental files are there in the path? ');

file_number=1;
inc_string=0;
file_base_name = file(1:end-4); 

while file_number <= (file_count + 1)
    str = num2str(file_number);
    
    if file_number > file_count
        file = file_base_name;
    elseif length(str) == 3
        file = strcat(file_base_name,'P',str);
    elseif length(str) == 2
        file = strcat(file_base_name,'P','0',str);
    elseif length(str) == 1
        file = strcat(file_base_name,'P','00',str);
    end
        
    last = load(file);
    Nx = last(length(last)-1,1);
    My = last(length(last)-1,2);
    u = last(2*My+1:3*My, 1:Nx);
    v = last(3*My+1:4*My, 1:Nx);
    if file_number == 1
        minu = min(min(u));
        minv = min(min(v));
        maxu = max(max(u));
        maxv = max(max(v));
    end
    currentminu = min(min(u));
    currentminv = min(min(v));
    currentmaxu = max(max(u));
    currentmaxv = max(max(v));
    minu = min([currentminu,minu]);
    minv = max([currentminv,minv]);
    maxu = min([currentmaxu,maxu]);
    maxv = max([currentmaxv,maxv]);
    
    last(length(last),15) = minu;
    last(length(last),16) = maxu;
    last(length(last),17) = minv;
    last(length(last),18) = maxv;
    
    backfilled = last;

    if file_number == file_count
        save(strcat(file,'_x','.mat'),'backfilled');
    end

    clear(file)
    clear tmp
    
    file_number = file_number + 1;
end






