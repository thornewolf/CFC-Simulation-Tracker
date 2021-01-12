% Image output naming scheme:
% '_A' corresponds to contour lines included
% '_B' corresponds to no contour lines included
% '_C' corresponds to the quiver plot.
% example: PfR21A1p90x8Y16n03_1_A
% Visualization code to generate images/frames of velocity flow fields based on output data 
% from ParabolaFlow
% 
% Variable Definitions:
%    x,y: point vectors
%    Nx,My: Number of points in the X and Y directions
%    s,S: velocity matrices
%    bx,by: boundaries
%    jet_range_index: position of synthetic jet
%    file_count: total number of files on path, nuber of last P### file
%    file_base_name: base name of files on path, no P###
%    image_name: name that figure will be saves as
%    file_number: index of what file to load on path
%    file: name of file to be loaded 
%    cbmin,cbmax: upper and lower limits of the colorbar
%    r: radius distance from origin
%    mu,eta: parabolic coordinate analogous to x and y in cartesian 
%    dmux,dmuy: cartesian grid spacing based off of parabolic coordinates
%    detx,dety: cartesian grid space based off of parabolic coordinates

close all;
clear;
clc;
graphics_toolkit gnuplot

function [file,file_base_name,file_count] = fileSelection
    % Ask for input of first file on path to determine file path and names 
    % from and how many files there are on path
    % 
    % Args: 
    %   none.
    % 
    % Return: 
    %   file,file_base_name,file_count
    
    fprintf('Choose the first P00# that you wish to start from.\n');
    file = input("File name: ",'s');
    file_base_name = file(1:end-4);

    % file_count is the amount of numbered files in the path. If the highest
    % number is P999 then the input to this should be 999.
    file_count = input('How many consecutive incremental files are there in the path? ');
endfunction

function [totalminu,totalmaxu,totalminv,totalmaxv] = detectBackfill(file_count,file_base_name)
    % determines whether to grab mins and maxes of u and v vectors directly from last output file, 
    % or from the .mat file created from the backfill.m code
    %
    % Args:
    %   file_count,file_base_name
    % 
    % Returns:
    %   totalminu,totalmaxu,totalminv,totalmaxv

     % determine name of the .mat file based on amount of files on path 
    str = num2str(file_count);
    if length(str) == 3
        matfile = strcat(file_base_name,'P',str,'_x.mat');
    elseif length(str) == 2
        matfile = strcat(file_base_name,'P','0',str,'_x.mat');
    elseif length(str) == 1
        matfile = strcat(file_base_name,'P','00',str,'_x.mat');
    end
    
    if exist(matfile,'file')
        % Mat file exists meaning backfill.m has been run on these files
        mat = load(matfile,'backfilled');
        totalminu = mat.backfilled(length(mat.backfilled),15);
        totalmaxu = mat.backfilled(length(mat.backfilled),16);
        totalminv = mat.backfilled(length(mat.backfilled),17);
        totalmaxv = mat.backfilled(length(mat.backfilled),18);
    else
        % File does not exist, mins and maxes exist in the output files
        tmp = load(file_base_name);
        totalminu = tmp(length(tmp),15);
        totalmaxu = tmp(length(tmp),16);
        totalminv = tmp(length(tmp),17);
        totalmaxv = tmp(length(tmp),18);
    end
endfunction

function file = nextFile(file_base_name,file_number,file_count)
    % Determine the name of the next file to load after counting up one
    % 
    % Args:
    %   file_base_name,file_number,file_count
    %   
    % Return:
    %   file

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
endfunction

function [cbmin,cbmax] = colorbarLimits2(file_count,file_base_name)
    % Determine the upper and lower limits of the color bar
    % 
    % Args: 
    %   file_count,file_base_name
    % 
    % Return:
    %   cbmin,cbmax

    [totalminu,totalmaxu,totalminv,totalmaxv] = detectBackfill(file_count,file_base_name);
    cbmin = -sqrt(totalminu^2 + totalminv^2)
    cbmax = sqrt(totalmaxu^2 + totalmaxv^2)
endfunction

function [dmux,dmuy,detx,dety] = gridSpacing(My,Nx,x,y,r,mu,eta)
    % Determine grid spacing of translated cartesian 
    %
    % Args:
    %   My,Nx,x,y,r,mu,eta
    % 
    % Return:
    %   dmux,dmuy,detx,dety

    % initialize
    dmux = zeros(My, Nx);
    dmuy = zeros(My, Nx);
    detx = zeros(My, Nx);
    dety = zeros(My, Nx);

    for j=2:My % 401
        for i=1:(Nx-1)/2 % 100
            dmux(j,i)=1/2*(x(j,i)/r(j,i)+1)/(mu(j,i));
            dmuy(j,i)=1/2*(y(j,i)/r(j,i))/mu(j,i) ;
            detx(j,i)=1/2*(x(j,i)/r(j,i)-1)/(eta(j,i));
            dety(j,i)=1/2*(y(j,i)/r(j,i))/eta(j,i) ;
        end
        for i= ((Nx-1)/2+2):Nx % 102:201
            dmux(j,i)=1/2*(x(j,i)/r(j,i)+1)/(mu(j,i));
            dmuy(j,i)=1/2*(y(j,i)/r(j,i))/mu(j,i) ;
            detx(j,i)=1/2*(x(j,i)/r(j,i)-1)/(eta(j,i));
            dety(j,i)=1/2*(y(j,i)/r(j,i))/eta(j,i) ;
        end
    end

    % average mu=0 line:
    for j=1:My % 401
        dmux(j,(Nx-1)/2+1)=(dmux(j,(Nx-1)/2)+dmux(j,(Nx-1)/2+2))/2;
        dmuy(j,(Nx-1)/2+1)=(dmuy(j,(Nx-1)/2)+dmuy(j,(Nx-1)/2+2))/2;
        detx(j,(Nx-1)/2+1)=(detx(j,(Nx-1)/2)+detx(j,(Nx-1)/2+2))/2;
        dety(j,(Nx-1)/2+1)=(dety(j,(Nx-1)/2)+dety(j,(Nx-1)/2+2))/2;
    end
endfunction

function jet_range_index = jetLocation(S)
    % Identity range of jet location from file data
    %
    % Args:
    %   S
    % 
    % Return:
    %   jet_range_index

    jet_start = S(length(S)-1,6); % Beginning of jet
    jet_end = S(length(S)-1,7); % End of jet
    jet_range_index = jet_start:jet_end;
endfunction

function s = velocityVctr(s,S,Nx,My,dmux,dmuy,detx,dety,mu,eta)
    % Calculate velicity vectors at each point
    % 
    % Args: 
    %   s,S,Nx,My,dmux,dmuy,detx,dety,mu,eta
    % 
    % Return: 
    %   s

    % Convert Velocity components P to C
    for j = (My*2+2):(3*My) % 804:1203
        for i = 1:Nx % 201
            S(j,i) = (s(j,i)*dety(j-(2*My),i)-s(j+My,i)*dmuy(j-(2*My),i))*sqrt(mu(j-(2*My),i)^2+eta(j-(2*My),i)^2);  %Vx
            S(j+My,i) = -(s(j,i)*detx(j-(2*My),i)-s(j+My,i)*dmux(j-(2*My),i))*sqrt(mu(j-(2*My),i)^2+eta(j-(2*My),i)^2); %Vy
        end
    end
    s=S;

    % Creates V-vctr from Vx and Vy
    for i = (length(S)-1):(length(S)-2)+My % 1605:2005
        for j = 1:((Nx-1)/2+1)
            s(i,j) = sqrt(s(i-(2*My),j)^2+s(i-My,j)^2);
        end
        for j = ((Nx-1)/2+1):Nx
            s(i,j) = sqrt(s(i-(2*My),j)^2+s(i-My,j)^2)*sign(s(i-(2*My),j));
        end
    end
endfunction

function [x,y,bx,by,r,mu,eta,S] = generateVectors(Nx,My,s)
    % Computations to go from physical parabolic coordinates to cartesian and identify boundaries
    %
    % Args:
    %   Nx,My,s
    % 
    % Return: 
    %   x,y,bx,by,r,mu,eta,S

    % change all values for mu<stagnation point (lower field) to -U
    % stag is the point closest to the stagnation point on lower surface
    stag = find(s((My*2+2),1:((Nx-1)/2+1))<0,1,'last');
    S=s;
    [mu,eta] = meshgrid(linspace(-20,20,Nx),linspace(1,11,My));
    x = 1/2*(mu.^2-eta.^2);
    y = mu.*eta;
    
    bx = 1/2*(mu(1,:).^2-1);
    by = mu(1,:);
    
    r = sqrt(x.^2+y.^2); % Vector transform from parabolic to Cartesian
endfunction


function createPlotA(x,y,Nx,My,s,S,bx,by,jet_range_index,file_count,file_base_name,image_name)
    % Plots velocity flow field over airfoil geometry, includes a colorbar and contour lines
    % and saves the figure and a .jpg that can be used as a frame for video.
    % 
    % Args: 
    %   x,y,Nx,My,s,S,bx,by,jet_range_index,file_count,file_base_name,image_name
    % 
    % Return:
    %   none. 
    
    % contour plot on V plot
    fig = figure('position',[0,0,1280,720]); % figure will have resulution of 720p
    [c,h]=contourf(x(1:((Nx-1)/2+1),:),y(1:((Nx-1)/2+1),:),s((length(S)-1):((length(S)-1)+(Nx-1)/2),:),100,'LineStyle', 'none');
    axis equal
    hold on
    plot(bx,by,'k','linewidth',1)
    if (S(length(S)-1,6) < Nx) && (S(length(S)-1,6) < Nx)
        plot(bx(jet_range_index),by(jet_range_index),'r-','linewidth',2) 
    end
    axis([-2 48 -4 12]) % V plot
    
    contour(x(1:((Nx-1)/2+1),:),y(1:((Nx-1)/2+1),:),s((length(S)-1):((length(S)-1)+(Nx-1)/2),:),25,'LineStyle', '-','LineColor','black');
    
    plot(bx,by,'k','linewidth',1);
    colorbar;
    colormap(jet); % sets color range of plot 
    axis([-2 16 -2 8]);
    [cbmin,cbmax] = colorbarLimits2(file_count,file_base_name);
    caxis([cbmin,cbmax]);
    imgName = strcat(image_name(1:end-4),'_A','.jpg');
    saveas(fig, char(imgName)) % save figure as a .jpg 
end

function createPlotB(x,y,Nx,My,s,S,bx,by,jet_range_index,file_count,file_base_name,image_name)
    % Plots velocity flow field over airfoil geometry, includes a colorbar
    % and saves the figure and a .jpg that can be used as a frame for video. There are
    % no contour lines included.
    % 
    % Args: 
    %   x,y,Nx,My,s,S,bx,by,jet_range_index,file_count,file_base_name,image_name
    % 
    % Return:
    %   none. 
    
    % contour plot on V plot
    fig = figure('position',[0,0,1280,720]); % figure will have resulution of 720p
    
    [C,h]=contourf(x(1:((Nx-1)/2+1),:),y(1:((Nx-1)/2+1),:),s((length(S)-1):((length(S)-1)+(Nx-1)/2),:),100,'LineStyle', 'none');
    axis equal
    hold on
    plot(bx,by,'k','linewidth',1)
    if (S(length(S)-1,6) < Nx) && (S(length(S)-1,6) < Nx)
        plot(bx(jet_range_index),by(jet_range_index),'r-','linewidth',2) 
    end
    axis([-2 48 -4 12]) % V plot

    plot(bx,by,'k','linewidth',1);
    colorbar;
    colormap(jet); % sets color range of plot 
    axis([-2 16 -2 8]);
    [cbmin,cbmax] = colorbarLimits2(file_count,file_base_name);
    caxis([cbmin,cbmax]);

    imgName = strcat(image_name(1:end-4),'_B','.jpg');
    saveas(fig, char(imgName)) % save figure as a .jpg 
end

function createPlotC(x,y,Nx,My,s,S,bx,by,jet_range_index,file_count,file_base_name,image_name)
    % Plots velocity flow field over airfoil geometry, includes a colorbar
    % and saves the figure and a .jpg that can be used as a frame for video. A quiver plot
    % is also plotted over the contour plot. 
    % 
    % Args: 
    %   x,y,Nx,My,s,S,bx,by,jet_range_index,file_count,file_base_name,image_name
    % 
    % Return:
    %   none. 

    % contour plot on V plot
    fig = figure('position',[0,0,1280,720]); % figure will have resulution of 720p
    
    hold on;
    [C,h]=contourf(x(1:((Nx-1)/2+1),:),y(1:((Nx-1)/2+1),:),s((length(S)-1):((length(S)-1)+(Nx-1)/2),:),100,'LineStyle', 'none');
    axis equal

    % plot quiver plot on top of contour plot
    % [u,v] = gradient(s((length(S)-1):((length(S)-1)+(Nx-1)/2),:),1,1);
    [u,v] = gradient((s((My+1):((My-1)/4)+(My+1),:)/(Nx-1)-1.5),1,1);
    % theta = atan(u./v);
    % U = cos(theta);
    % V = sin(theta);
    q = quiver(x(5:20:((Nx-1)/2+1),1:2:Nx),y(5:20:((Nx-1)/2+1),1:2:Nx),u(5:20:end,1:2:Nx),v(5:20:end,1:2:Nx),0.1);
    
    #q.Color = 'black';
    #q.LineWidth = 1;
    plot(bx,by,'k','linewidth',1)
    axis equal
    if (S(length(S)-1,6) < Nx) && (S(length(S)-1,6) < Nx)
        plot(bx(jet_range_index),by(jet_range_index),'r-','linewidth',2) 
    end
    axis([-2 48 -4 12]) % V plot
    plot(bx,by,'k','linewidth',1);
    colorbar;
    colormap(jet); % sets color range of plot 
    axis([-2 16 -2 8]);
    [cbmin,cbmax] = colorbarLimits2(file_count,file_base_name);
    caxis([cbmin,cbmax]);
    imgName = strcat(image_name(1:end-4),'_C','.jpg');
    saveas(fig, char(imgName)) % save figure as a .jpg 
end

[file,file_base_name,file_count] = fileSelection;

file_number = 1;
while file_number <= (file_count + 1)
    % determine name of image that corresponds with output file
    rand_file_number = randi(file_count)
    disp('Starting (iteration, file_number)')
    disp(file_number)
    disp(rand_file_number)
    image_name = [file_base_name '_' num2str(rand_file_number) '.jpg'];
    if exist(image_name,'file') == 2 % if image name already exists, program will end
        file_number = file_number + 1;
        continue
    end
    file = nextFile(file_base_name,rand_file_number,file_count); 
    disp('about to load file');
    s = load(file);
    disp('loaded file');
    Nx = s(length(s)-1,1);
    My = s(length(s)-1,2);
    [x,y,bx,by,r,mu,eta,S] = generateVectors(Nx,My,s);
    disp(My)
    disp(Nx)

    [dmux,dmuy,detx,dety] = gridSpacing(My,Nx,x,y,r,mu,eta);
    s = velocityVctr(s,S,Nx,My,dmux,dmuy,detx,dety,mu,eta);
    jet_range_index = jetLocation(S);

    createPlotA(x,y,Nx,My,s,S,bx,by,jet_range_index,file_count,file_base_name,image_name);
    close
    createPlotB(x,y,Nx,My,s,S,bx,by,jet_range_index,file_count,file_base_name,image_name);
    close
    createPlotC(x,y,Nx,My,s,S,bx,by,jet_range_index,file_count,file_base_name,image_name);
    close

    file_number = file_number + 1;
    clear(file)
end

close all


