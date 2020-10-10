close all;clc;clear all;
graphics_toolkit gnuplot

fprintf('Choose the first P00# that you wish to start from.\n')
file = input("File name:")
% [file,path]=uigetfile('*.*');
original_file_name = file;
fill=length(file);

file_number=1;
inc_string=0;

video_base_name = file(1:end-4);
file_base_name = file(1:end-4);

% file_count is the amount of numbered files in the path. If the highest
% number is P999 then the input to this should be 999.
file_count = input('How many consecutive incremental files are there in the path? ');

% Variables to store the global minumum and maximum values of O, P, U, V.
MINO = 0;
MAXO = 0;
MINP = 0;
MAXP = 0;
MINU = 0;
MAXU = 0;
MINV = 0;
MAXV = 0;

matfile = strcat(file_base_name,'_x','.mat');
if exist(matfile)
    % Mat file exists -> backfill has been run on these files
    mat = load(matfile,'backfilled');
    totalminu = mat.backfilled(length(mat.backfilled),15);
    totalmaxu = mat.backfilled(length(mat.backfilled),16);
    totalminv = mat.backfilled(length(mat.backfilled),17);
    totalmaxv = mat.backfilled(length(mat.backfilled),18);
else
    % File does not exist.
    tmp = load(file_base_name);
    totalminu = tmp(length(tmp),15);
    totalmaxu = tmp(length(tmp),16);
    totalminv = tmp(length(tmp),17);
    totalmaxv = tmp(length(tmp),18);
end


file_number = 1;
file = original_file_name;

function [ ret ] = getframe (h)

  print (h, "tmp.fig", "-dppm");
  ret = im2double (imread ("tmp.fig"));
  ## Truncate to even size to accomodate addframe()
  if (mod (size (ret, 1), 2) > 0); ret = ret(2:end, :, :); endif
  if (mod (size (ret, 2), 2) > 0); ret = ret(:, 2:end, :); endif

endfunction

while file_number <= (file_count + 1)
    image_name = [file_base_name '_' num2str(file_number) '.jpg'];
    if exist(image_name,'file')==2
        file_number = file_number + 1;
        continue
    end
    
    inc_string=num2str(file_number);
    fp=length(inc_string);
    
    if fp==1
        file(fill)=inc_string(1);
    elseif fp==2
        file(fill)=inc_string(2);
        file(fill-1)=inc_string(1);
    elseif fp==3
        file(fill)=inc_string(3);
        file(fill-1)=inc_string(2);
        file(fill-2)=inc_string(1);
    end
    
    if file_number > file_count
        file = file_base_name;
    end
    
    disp('about to load file')
    % load(file)
    %eval(['s=' file ';'])
    s = load(file);
    disp('loaded file')
    
    % change all values for mu<stagnation point (lower field) to -U
    % stag is the point closest to the stagnation point on lower surface
    Nx = s(length(s)-1,1);
    My = s(length(s)-1,2);
    
    stag = find(s((My*2+2),1:((Nx-1)/2+1))<0,1,'last');
    S=s;
    
    [mu,eta]=meshgrid(linspace(-20,20,Nx),linspace(1,11,My));
    
    x=1/2*(mu.^2-eta.^2);
    y=mu.*eta;
    
    bx=1/2*(mu(1,:).^2-1);
    by=mu(1,:);
    
    %   Vector transform from parabolic to Cartesian
    r=sqrt(x.^2+y.^2);
    
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

    
    % Convert Velocity components P to C
    for j=(My*2+2):(3*My) % 804:1203
        for i=1:Nx % 201
            S(j,i)=(s(j,i)*dety(j-(2*My),i)-s(j+My,i)*dmuy(j-(2*My),i))*sqrt(mu(j-(2*My),i)^2+eta(j-(2*My),i)^2);  %Vx
            S(j+My,i)=-(s(j,i)*detx(j-(2*My),i)-s(j+My,i)*dmux(j-(2*My),i))*sqrt(mu(j-(2*My),i)^2+eta(j-(2*My),i)^2); %Vy
        end
    end
    s=S;

    % Creates V-vctr from Vx and Vy
    for i=(length(S)-1):(length(S)-2)+My % 1605:2005
        for j=1:((Nx-1)/2+1)
            s(i,j)=sqrt(s(i-(2*My),j)^2+s(i-My,j)^2);
        end
        for j=((Nx-1)/2+1):Nx
            s(i,j)=sqrt(s(i-(2*My),j)^2+s(i-My,j)^2)*sign(s(i-(2*My),j));
        end
    end

    jet_start = S(length(S)-1,6);
    jet_end = S(length(S)-1,7);
    jet_range_index = jet_start:jet_end;
    
    % contour plot on V plot
    % fig = figure('position',[0,0,1920,1080], "visible", "off")
    fig = figure()
    #caxis([MINO MAXO])
    disp(MINO)
    disp(MAXO)
    #caxis([-5 5])
    [C,h]=contourf(x(1:((Nx-1)/2+1),:),y(1:((Nx-1)/2+1),:),s((length(S)-1):((length(S)-1)+(Nx-1)/2),:),100);
    axis equal
    hold on
    plot(bx,by,'k','linewidth',1)
    if (S(length(S)-1,6) < Nx) && (S(length(S)-1,6) < Nx)
        plot(bx(jet_range_index),by(jet_range_index),'r-','linewidth',2) 
    end
    colorbar
    axis([-2 48 -4 12]) %V plot
    %contour(x(1:((Nx-1)/2+1),:),y(1:((Nx-1)/2+1),:),(s((My+1):((My-1)/4)+(My+1),:)/(Nx-1)-1.5),((Nx-1)/2))
    plot(bx,by,'k','linewidth',1)

    colorbar
    axis([-2 16 -2 8])
    
    max_mag_x = max(abs([totalminu,totalmaxu]));
    max_mag_y = max(abs([totalminv,totalmaxv]));
    colorbar_limit = sqrt(max_mag_x^2 + max_mag_y^2);
    disp(colorbar_limit)
    caxis([-colorbar_limit*2,colorbar_limit*2]);
    
    saveas(fig, char(image_name))
    %F = getframe(gcf);
    %[X, map] = frame2im(F);
    %imwrite(X,char(image_name))
    
    % print -djpg image_name
    close
    
    file_number = file_number + 1;
    
    clear(file)
end


close all

##Defunct movie code due to the fact that Octave does not have these 
##capabilities.
##videoName = [video_base_name '.mp4'];
##mov = VideoWriter(videoName, 'MPEG-4');
##mov.Quality = 100;
##mov.FrameRate = 15;
##open(mov)
##
##
##file_number = 1;
##while file_number <= (file_count + 1)
##    image_name = [file_base_name '_' num2str(file_number) '.jpg'];
##    writeVideo(mov,imread(image_name));
##    file_number = file_number + 1;
##end
##
##close(mov)

